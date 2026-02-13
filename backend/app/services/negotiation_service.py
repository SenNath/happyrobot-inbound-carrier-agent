from decimal import Decimal, ROUND_HALF_UP
from typing import Literal

from app.models import Load


class NegotiationService:
    def evaluate_offer(
        self,
        load: Load | None,
        carrier_offer: Decimal,
        round_number: int,
        previous_counter_rate: Decimal | None = None,
    ) -> tuple[Literal["accept", "counter", "reject", "needs_more_info"], Decimal | None, str]:
        if load is None:
            return "needs_more_info", None, "Unknown load_id; cannot evaluate without a valid load context."

        if carrier_offer <= 0:
            return "needs_more_info", None, "Carrier offer must be a positive amount."

        target_rate = Decimal(load.loadboard_rate)
        accept_threshold = (target_rate * Decimal("1.02")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        hard_reject_threshold = (target_rate * Decimal("1.15")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        if carrier_offer <= accept_threshold:
            return "accept", None, "Offer is within accepted rate tolerance."

        if round_number >= 3 and carrier_offer > (target_rate * Decimal("1.10")):
            return "reject", None, "Final negotiation round exceeded acceptable premium threshold."

        if carrier_offer >= hard_reject_threshold:
            return "reject", None, "Offer is materially above market baseline."

        # Keep negotiation progression monotonic across rounds:
        # when available, anchor midpoint to the last counter rather than resetting to loadboard rate.
        anchor_rate = target_rate
        if previous_counter_rate is not None:
            anchor_rate = max(target_rate, Decimal(previous_counter_rate))

        counter_raw = (carrier_offer + anchor_rate) / 2
        counter_cap = (target_rate * Decimal("1.06"))
        counter_rate = min(counter_raw, counter_cap).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        if previous_counter_rate is not None:
            prior_counter = Decimal(previous_counter_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            counter_rate = max(counter_rate, prior_counter)

        return "counter", counter_rate, "Countering toward indexed market rate."
