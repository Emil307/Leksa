"""Доменная сущность реферальной программы."""

from typing import Optional

from domain.entities._base import DomainEntity


class Referral(DomainEntity):
    """Реферальная связь между пользователями."""

    id: Optional[int] = None
    referrer_id: int
    referred_id: int
    bonus_applied: bool = False
