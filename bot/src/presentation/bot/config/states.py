"""FSM-состояния бота."""

from aiogram.fsm.state import State, StatesGroup


class IdiomTestState(StatesGroup):
    """Состояния для теста на идиомы."""

    in_progress: State = State()
    awaiting_answer: State = State()


class GrammarGameState(StatesGroup):
    """Состояния для игры Грамматикус."""

    in_progress: State = State()
    awaiting_answer: State = State()


class PromoCodeState(StatesGroup):
    """Состояния для ввода промокода."""

    waiting_for_code: State = State()
