from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence


@dataclass(frozen=True)
class VisionMetadata:
    """Represent normalized metadata returned by the vision model.

    Parameters:
        description: Short textual summary of the image contents.
        keywords: Search-oriented ingredient tags returned by the model.

    Returns:
        VisionMetadata: Structured metadata ready for persistence.

    Raises:
        None.

    Example:
        >>> VisionMetadata(description="Fresh basil", keywords=("basil",))
        VisionMetadata(description='Fresh basil', keywords=('basil',))
    """

    description: str
    keywords: Sequence[str]


class VisionClient:
    """Wrap an OpenAI vision endpoint behind a small mockable adapter.

    Parameters:
        model: Fully qualified vision model name to call.
        http_client: Injectable HTTP client exposing a `post` method.
        api_base: Base URL for the OpenAI API.
        retries: Maximum retry attempts for transient failures.

    Returns:
        VisionClient: Configured client wrapper for metadata extraction.

    Raises:
        None.

    Example:
        >>> VisionClient(model="gpt-4.1-mini", http_client=object())
        <...VisionClient object...>
    """

    API_PATH = "/v1/vision/describe"
    SUPPORTED_EXTENSIONS = {"jpg", "jpeg", "png", "webp", "tiff", "heic"}

    def __init__(
        self,
        model: str,
        http_client: Any | None = None,
        api_base: str = "https://api.openai.com",
        retries: int = 3,
    ) -> None:
        """Initialize the vision client with required configuration.

        Parameters:
            model: Vision model name, e.g., "gpt-5.1-vision".
            http_client: HTTP client implementing .post(...) used for API calls.
            api_base: API base URL for OpenAI requests.
            retries: Maximum retry attempts for transient failures.

        Returns:
            None.

        Raises:
            None.

        Example:
            >>> VisionClient(model="gpt-4.1-mini", http_client=object())
            <...VisionClient object...>
        """

        self.model = model
        self.api_base = api_base.rstrip("/")
        self.retries = max(1, retries)
        self._http_client = http_client

    def analyze_image(self, image_path: Path) -> VisionMetadata:
        """Send the image bytes to OpenAI and return normalized metadata.

        Parameters:
            image_path: Path to the image file to describe.

        Returns:
            VisionMetadata: Structured description and keywords for the input image.

        Raises:
            RuntimeError: When no http_client was configured.
            ValueError: When the response omits required metadata.

        Example:
            >>> client = VisionClient(model="gpt-4.1-mini", http_client=object())
            >>> client.analyze_image(Path("ingredient.png"))
        """

        if self._http_client is None:
            raise RuntimeError("An http_client is required to execute API calls.")

        payload = self._build_payload(image_path)
        response = self._post_with_retry(payload)
        return self._parse_response(response)

    def _build_payload(self, image_path: Path) -> Mapping[str, Any]:
        """Create the request payload including model name and image bytes.

        Parameters:
            image_path: Path to the image file to encode.

        Returns:
            Mapping[str, Any]: Request payload for the mocked OpenAI endpoint.

        Raises:
            ValueError: If the file extension is unsupported.
            OSError: If the image file cannot be read.

        Example:
            >>> VisionClient(model="x", http_client=object())._build_payload(Path("a.png"))
        """

        extension = image_path.suffix.lstrip(".").lower()
        if extension not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported image extension: {extension}")

        with image_path.open("rb") as handle:
            content = handle.read()

        return {
            "model": self.model,
            "files": [
                {
                    "name": image_path.name,
                    "data": content,
                }
            ],
        }

    def _post_with_retry(self, payload: Mapping[str, Any]) -> Any:
        """Execute the request with retries while keeping the transport injectable.

        Parameters:
            payload: JSON-serializable request payload.

        Returns:
            Any: Raw response object returned by the injected HTTP client.

        Raises:
            RuntimeError: If every retry attempt fails.

        Example:
            >>> client = VisionClient(model="x", http_client=object())
            >>> client._post_with_retry({"model": "x"})
        """

        url = f"{self.api_base}{self.API_PATH}"
        headers = {"Content-Type": "application/json"}
        last_error: Exception | None = None

        for attempt in range(self.retries):
            try:
                # Http clients should expose a .post method with signature similar to requests.
                return self._http_client.post(url, json=payload, headers=headers)
            except Exception as exc:
                last_error = exc

        raise RuntimeError("Unable to reach the OpenAI vision endpoint.") from last_error

    def _parse_response(self, response: Any) -> VisionMetadata:
        """Extract description and keywords from the API response object.

        Parameters:
            response: Response object exposing a `json()` method.

        Returns:
            VisionMetadata: Normalized metadata extracted from the payload.

        Raises:
            ValueError: If the payload shape is invalid or incomplete.

        Example:
            >>> class Response:
            ...     def json(self):
            ...         return {"data": [{"description": "x", "keywords": ["y"]}]}
            >>> VisionClient(model="x", http_client=object())._parse_response(Response())
            VisionMetadata(description='x', keywords=('y',))
        """

        if not hasattr(response, "json"):
            raise ValueError("Response object must implement json().")

        decoded = response.json()
        data = decoded.get("data")
        if not isinstance(data, list) or not data:
            raise ValueError("Response payload missing data list.")

        entry = data[0]
        if not isinstance(entry, Mapping):
            raise ValueError("Response payload must contain object entries.")
        description = entry.get("description")
        keywords = entry.get("keywords")

        if not isinstance(description, str) or not isinstance(keywords, list):
            raise ValueError("Missing required description or keywords fields.")

        return VisionMetadata(description=description, keywords=tuple(str(tag) for tag in keywords))
