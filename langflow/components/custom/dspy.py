import json
from typing import Any

import dspy
from langchain_openai import ChatOpenAI
from langflow.custom.custom_component.component import Component
from langflow.inputs import HandleInput, MessageTextInput
from langflow.io import CodeInput, Output
from langflow.schema.data import Data
from langflow.schema.message import Message
from pydantic import SecretStr

'''
## Example1:
> One input, one output field.

```py
class Sentiment(dspy.Signature):
    """Classify the sentiment of a given sentence."""

    sentence: str = dspy.InputField()
    sentiment: str = dspy.OutputField(desc="positive, negative, or neutral")
```

- input: I love this movie, it was fantastic!
- output: { "sentiment": "positive" }

## Example2:
> One input, multiple specific output fields.

```py
class AspectSentiment(dspy.Signature):
    """Extract specific aspect, its sentiment, and the supporting reason from a sentence."""

    sentence: str = dspy.InputField()
    aspect: str = dspy.OutputField(desc="the specific feature of the movie being discussed")
    sentiment: str = dspy.OutputField(desc="positive, negative, or neutral")
    reason: str = dspy.OutputField(desc="the specific phrase from the text supporting the sentiment")
```

- input: The special effects in the movie were breathtaking, but the plot was predictable and the ending felt rushed.
- output: { "aspect": "visual effects", "sentiment": "positive", "reason": "breathtaking" }

## Example3:
> Multiple inputs, multiple output fields.

```py
class ContextualAnalysis(dspy.Signature):
    """Analyze the review based on specific movie context to identify focus and emotional depth."""

    sentence: str = dspy.InputField(desc="The user review text")
    movie_context: str = dspy.InputField(desc="Additional background like director or genre")

    primary_focus: str = dspy.OutputField(desc="What the review is mainly about (e.g., acting, directing, atmosphere)")
    emotional_depth: str = dspy.OutputField(desc="How intense the emotion is: low, medium, or high")
    key_takeaway: str = dspy.OutputField(desc="A brief summary of the user's final verdict")
```

- input:
  - sentence: I've been waiting for this sequel for years, and it absolutely exceeded every single expectation I had! I'm still shaking from the excitement.
  - movie_context: Directed by Denis Villeneuve, Sci-Fi epic.
- output: { "primary_focus": "overall quality and expectations", "emotional_depth": "high", "key_takeaway": "An overwhelming success that surpassed years of anticipation." }
'''

DEFAULT_SIGNATURE_CODE = '''
import dspy


class Sentiment(dspy.Signature):
    """Classify the sentiment of a given sentence."""

    sentence: str = dspy.InputField()
    sentiment: str = dspy.OutputField(desc="positive, negative, or neutral")
'''.strip()


class DSPyComponent(Component):
    name = "DSPy"
    display_name = "DSPy"
    description = "Run a DSPy Signature (optionally restoring program state JSON)."
    icon = "sparkles"

    inputs = [
        MessageTextInput(
            name="query",
            display_name="Query",
            info="Text query to feed into the Signature's first input field.",
            value="I love this movie, it was fantastic!",
            required=True,
        ),
        CodeInput(
            name="signature_code",
            display_name="Signature Code",
            info="Python code that defines a dspy.Signature subclass.",
            real_time_refresh=True,
            value=DEFAULT_SIGNATURE_CODE,
        ),
        HandleInput(
            name="program_state_json",
            display_name="Program State JSON",
            info="Compiled program state as JSON (Message or Data). Optional.",
            input_types=["Message", "Data"],
            required=False,
        ),
        HandleInput(
            name="llm",
            display_name="Language Model",
            info="The language model to use to generate the structured output.",
            input_types=["LanguageModel"],
            required=True,
        ),
    ]

    outputs = [
        Output(
            display_name="Result",
            name="message_output",
            method="generate_message_output",
        ),
        Output(
            display_name="Result",
            name="data_output",
            method="generate_data_output",
        ),
    ]

    def _get_model_param(self) -> dict[str, Any]:
        model = self.llm
        # LocalOpenAI/OpenAI
        if isinstance(model, ChatOpenAI):
            raw: dict[str, Any] = model.model_dump(exclude_none=True)
            model_name: str = raw.pop("model_name", None)
            if not model_name.startswith("openai/"):
                model_name = f"openai/{model_name}"
            return {
                "model": model_name,
                "api_base": raw.pop("openai_api_base", None),
                "api_key": raw.pop("openai_api_key", None),
                **raw,
            }
        return {}

    async def _run_predict(self) -> tuple[dict[str, Any], str]:
        signature_cls = _extract_signature_from_code(self.signature_code)

        # DSPy Signatures provide structured input/output field metadata.
        input_fields = getattr(signature_cls, "input_fields", None)
        if not input_fields:
            msg = "Signature must define at least one InputField."
            raise ValueError(msg)
        input_name: str = next(iter(input_fields.keys()))

        output_fields = getattr(signature_cls, "output_fields", None)
        if not input_fields:
            msg = "Signature must define at least one OutputField."
            raise ValueError(msg)
        output_name: str = next(iter(output_fields.keys()))

        model_params = self._get_model_param()
        model_name = model_params.get("model")
        if not model_name:
            msg = "A model selection is required"
            raise ValueError(msg)
        api_base = model_params.get("api_base")
        api_key = model_params.get("api_key")
        if isinstance(api_key, SecretStr):
            api_key = api_key.get_secret_value()

        lm = dspy.LM(
            model_name,
            api_base=api_base,
            api_key=api_key,
            extra_body={
                "reasoning_effort": "none",
                "chat_template_kwargs": {
                    "enable_thinking": False,
                },
                "temperature": 0,
            },
        )

        with dspy.context(lm=lm):
            program = dspy.Predict(signature_cls)

            state = _state_to_dict(getattr(self, "program_state_json", None))
            if state and hasattr(program, "load_state"):
                # Restore compiled/teleprompted parameters if available.
                program.load_state(state)  # type: ignore[attr-defined]

            pred = program(**{input_name: self.query})

        # Normalize prediction to dict for downstream nodes.
        if isinstance(pred, dict):
            pred_dict = pred
        elif hasattr(pred, "toDict"):
            pred_dict = pred.toDict()  # type: ignore[attr-defined]
        elif hasattr(pred, "__dict__"):
            pred_dict = dict(getattr(pred, "__dict__", {}))
        else:
            pred_dict = {"value": pred}

        text = pred_dict.get(output_name) or json.dumps(pred_dict, ensure_ascii=False)
        return pred_dict, str(text)

    async def generate_message_output(self) -> Message:
        pred_dict, text = await self._run_predict()
        # Show both a short text and full JSON for easy inspection.
        if pred_dict and pred_dict != {"value": text}:
            payload = {"text": text, "prediction": pred_dict}
            return Message(
                text="```json\n"
                + json.dumps(payload, ensure_ascii=False, indent=2)
                + "\n```"
            )
        return Message(text=text)

    async def generate_data_output(self) -> Data:
        pred_dict, _ = await self._run_predict()
        return Data(data=pred_dict)


def _json_loads_maybe(s: str) -> Any:
    s0 = (s or "").strip()
    if not s0:
        return None
    return json.loads(s0)


def _extract_signature_from_code(signature_code: str) -> type[dspy.Signature]:
    namespace: dict[str, Any] = {}
    # Execute user-provided Signature definition (DSPy expects real Python objects).
    exec(compile(signature_code, "<dspy_signature>", "exec"), namespace)

    # Pick the last public Signature subclass defined in the snippet.
    candidates: list[type[dspy.Signature]] = []
    for name, obj in namespace.items():
        if name.startswith("_"):
            continue
        if isinstance(obj, type) and issubclass(obj, dspy.Signature):
            if obj is not dspy.Signature:
                candidates.append(obj)
    if not candidates:
        msg = "No dspy.Signature subclass found in Signature code."
        raise ValueError(msg)
    return candidates[-1]


def _state_to_dict(program_state: Any) -> dict[str, Any] | None:
    if program_state is None or program_state == "":
        return None

    if isinstance(program_state, Message):
        raw = program_state.text
        if isinstance(raw, str) and raw.strip():
            loaded = _json_loads_maybe(raw)
            return loaded if isinstance(loaded, dict) else {"value": loaded}
        return None

    if isinstance(program_state, Data):
        return program_state.data

    if isinstance(program_state, dict):
        return program_state

    if isinstance(program_state, str):
        loaded = _json_loads_maybe(program_state)
        return loaded if isinstance(loaded, dict) else {"value": loaded}

    return {"value": program_state}
