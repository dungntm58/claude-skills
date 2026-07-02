"""Nano Banana image API client. Model IDs are the single source of truth;
bump them here if Google changes the strings."""
import base64
import json
import os
import urllib.request

FLASH = "gemini-3.1-flash-image"   # Nano Banana 2 (default)
PRO = "gemini-3-pro-image"         # Nano Banana Pro (--pro)

# Project-level key file. A project's .nano-banana.env (found by walking up from
# the cwd) overrides the global GEMINI_API_KEY / GOOGLE_API_KEY environment.
DOTFILE = ".nano-banana.env"


def model_id(pro=False):
    return PRO if pro else FLASH


def _find_dotfile(start_dir):
    """Return the nearest DOTFILE, walking `start_dir` up to the filesystem
    root, or None if not found."""
    d = os.path.abspath(start_dir)
    while True:
        cand = os.path.join(d, DOTFILE)
        if os.path.isfile(cand):
            return cand
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent


def _parse_env_file(path):
    """Parse a KEY=VALUE dotfile into a dict. Ignores blank lines and
    `#` comments; tolerates a leading `export ` and surrounding quotes."""
    values = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            if line.startswith("export "):
                line = line[len("export "):]
            k, v = line.split("=", 1)
            values[k.strip()] = v.strip().strip('"').strip("'")
    return values


def _key_from(source):
    """First of GEMINI_API_KEY / GOOGLE_API_KEY present in a dict-like source."""
    return source.get("GEMINI_API_KEY") or source.get("GOOGLE_API_KEY")


def resolve_key(env=None, project_dir=None):
    """Resolve the API key across two levels. A project's `.nano-banana.env`
    (found by walking `project_dir` — or the cwd — up to the filesystem root)
    takes precedence over the global environment (GEMINI_API_KEY, then
    GOOGLE_API_KEY). Raises RuntimeError if neither yields a key."""
    env = os.environ if env is None else env
    dotfile = _find_dotfile(project_dir or os.getcwd())
    if dotfile:
        key = _key_from(_parse_env_file(dotfile))
        if key:
            return key
    key = _key_from(env)
    if key:
        return key
    raise RuntimeError(
        "No API key found. Set GEMINI_API_KEY or GOOGLE_API_KEY, or add one to "
        f"a {DOTFILE} file in your project."
    )


_REST_ENDPOINT = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "{model}:generateContent"
)


def _extract_png_from_rest(payload):
    """Pull the first inline image's bytes out of a generateContent response."""
    for cand in payload.get("candidates", []):
        for part in cand.get("content", {}).get("parts", []):
            inline = part.get("inlineData") or part.get("inline_data")
            if inline and inline.get("data"):
                return base64.b64decode(inline["data"])
    raise RuntimeError("API response contained no image data")


def _generate_rest(prompt, model, key, reference_images):
    parts = [{"text": prompt}]
    for img_bytes in reference_images or []:
        parts.append({
            "inlineData": {
                "mimeType": "image/png",
                "data": base64.b64encode(img_bytes).decode("ascii"),
            }
        })
    body = json.dumps({"contents": [{"parts": parts}]}).encode("utf-8")
    url = _REST_ENDPOINT.format(model=model)
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json", "x-goog-api-key": key},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    return _extract_png_from_rest(payload)


def _generate_sdk(prompt, model, key, reference_images):
    from google import genai  # type: ignore[import-not-found]
    from google.genai import types  # type: ignore[import-not-found]

    client = genai.Client(api_key=key)
    contents = [prompt]
    for img_bytes in reference_images or []:
        contents.append(
            types.Part.from_bytes(data=img_bytes, mime_type="image/png")
        )
    resp = client.models.generate_content(model=model, contents=contents)
    for part in resp.candidates[0].content.parts:
        if getattr(part, "inline_data", None) and part.inline_data.data:
            return part.inline_data.data
    raise RuntimeError("API response contained no image data")


def generate_image(prompt, model=FLASH, reference_images=None, env=None, key=None):
    """Generate a PNG (bytes) from a text prompt and optional reference images
    (list of PNG bytes). Uses the google-genai SDK when importable, else raw
    REST over stdlib. `env`/`key` are injectable for testing."""
    if not prompt or not prompt.strip():
        raise ValueError("prompt must be non-empty")
    if key is None:
        key = resolve_key(env)
    try:
        return _generate_sdk(prompt, model, key, reference_images)
    except ImportError:
        return _generate_rest(prompt, model, key, reference_images)
