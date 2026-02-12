from app.services.fmcsa_client import FMCSAClient, FMCSAResult


class CarrierService:
    def __init__(self, fmcsa_client: FMCSAClient) -> None:
        self.fmcsa_client = fmcsa_client

    async def verify(self, mc_number: str) -> FMCSAResult:
        return await self.fmcsa_client.verify_carrier(mc_number)
