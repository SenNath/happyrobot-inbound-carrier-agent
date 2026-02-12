from dataclasses import dataclass

import httpx


class FMCSAServiceError(RuntimeError):
    pass


@dataclass
class FMCSAResult:
    eligible: bool
    verification_status: str


class FMCSAClient:
    BASE_URL = "https://mobile.fmcsa.dot.gov/qc/services"

    def __init__(self, api_key: str, timeout_seconds: float = 8.0) -> None:
        self.api_key = api_key
        self.timeout_seconds = timeout_seconds

    async def verify_carrier(self, mc_number: str) -> FMCSAResult:
        if not self.api_key:
            raise FMCSAServiceError("FMCSA_API_KEY is not configured")

        endpoints = [
            f"{self.BASE_URL}/carriers/{mc_number}",
            f"{self.BASE_URL}/carriers/docket-number/{mc_number}",
        ]

        last_error: Exception | None = None
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            for endpoint in endpoints:
                try:
                    response = await client.get(endpoint, params={"webKey": self.api_key})
                    response.raise_for_status()
                    payload = response.json()
                    result = self._parse_payload(payload)
                    if result:
                        return result
                except (httpx.HTTPError, ValueError, KeyError, TypeError) as exc:
                    last_error = exc
                    continue

        raise FMCSAServiceError(f"Unable to verify carrier from FMCSA: {last_error}")

    def _parse_payload(self, payload: dict) -> FMCSAResult | None:
        content = payload.get("content")
        if not content:
            return None

        carrier: dict | None = None
        if isinstance(content, list) and content:
            carrier = content[0].get("carrier") if isinstance(content[0], dict) else None
        elif isinstance(content, dict):
            carrier = content.get("carrier") or content

        if not isinstance(carrier, dict):
            return None

        allowed_to_operate = str(carrier.get("allowedToOperate", "")).lower() in {"true", "yes", "1"}
        out_of_service = str(carrier.get("outOfServiceDate", "")).strip() != ""
        operating_status = str(carrier.get("statusCode", "") or carrier.get("status", "")).upper()

        in_service_statuses = {"A", "ACTIVE", "AUTHORIZED"}
        eligible = allowed_to_operate and (not out_of_service) and (operating_status in in_service_statuses)

        status = "eligible" if eligible else "ineligible"
        return FMCSAResult(eligible=eligible, verification_status=status)
