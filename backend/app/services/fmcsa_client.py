from dataclasses import dataclass

import httpx


class FMCSAServiceError(RuntimeError):
    pass


@dataclass
class FMCSAResult:
    eligible: bool
    verification: str
    legal_name: str | None
    mc_number: str


class FMCSAClient:
    BASE_URL = "https://mobile.fmcsa.dot.gov/qc/services"

    def __init__(self, api_key: str, timeout_seconds: float = 8.0) -> None:
        self.api_key = api_key
        self.timeout_seconds = timeout_seconds

    async def verify_carrier(self, mc_number: str) -> FMCSAResult:
        if not self.api_key:
            raise FMCSAServiceError("FMCSA_API_KEY is not configured")

        normalized_mc = self._normalize_mc_number(mc_number)
        endpoint = f"{self.BASE_URL}/carriers/docket-number/{normalized_mc}"
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            try:
                response = await client.get(endpoint, params={"webKey": self.api_key})
                response.raise_for_status()
                payload = response.json()
                return self._parse_payload(payload, normalized_mc)
            except (httpx.HTTPError, ValueError, KeyError, TypeError) as exc:
                raise FMCSAServiceError(f"Unable to verify carrier from FMCSA: {exc}") from exc

    def _parse_payload(self, payload: dict, mc_number: str) -> FMCSAResult:
        content = payload.get("content")
        if not content:
            return FMCSAResult(
                eligible=False,
                verification="invalid_mc",
                legal_name=None,
                mc_number=mc_number,
            )

        carrier: dict | None = None
        if isinstance(content, list) and content:
            carrier = content[0].get("carrier") if isinstance(content[0], dict) else None
        elif isinstance(content, dict):
            carrier = content.get("carrier") or content

        if not isinstance(carrier, dict):
            return FMCSAResult(
                eligible=False,
                verification="invalid_mc",
                legal_name=None,
                mc_number=mc_number,
            )

        allowed_to_operate = str(carrier.get("allowedToOperate", "")).upper() == "Y"
        authority_status = str(carrier.get("statusCode", "")).upper()
        eligible = allowed_to_operate and authority_status == "A"
        verification = "verified" if eligible else "not_authorized"

        return FMCSAResult(
            eligible=eligible,
            verification=verification,
            legal_name=carrier.get("legalName"),
            mc_number=mc_number,
        )

    def _normalize_mc_number(self, mc_number: str) -> str:
        normalized = "".join(ch for ch in mc_number if ch.isdigit())
        return normalized or mc_number.strip()
