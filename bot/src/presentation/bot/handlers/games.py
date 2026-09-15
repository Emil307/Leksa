"""
Хендлеры для игр.
"""
from aiogram import Dispatcher, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from domain.entities.user import User
from domain.entities.idiom import Idiom
from domain.entities.grammar_question import GrammarQuestion

from presentation.bot.config import messages
from presentation.bot.config.callbacks.games import (
    GamesMenuCallback,
    GameSelectCallback,
    GameStartCallback,
    GrammarLevelCallback,
    GameAnswerCallback,
)
from presentation.bot.config.builders.games_builder import GamesBuilder, LETTERS
from presentation.bot.config.builders.menu import MenuBuilder
from presentation.bot.config.states import GrammarGameState, IdiomTestState

from application.services.grammar_question import get_grammar_question_service
from application.services.idiom import get_idiom_service
from application.services.test import get_test_service
from application.services.game_thread import get_game_thread_service

from presentation.bot.utils.file_helpers import cache_game_media, get_game_media
from presentation.bot.utils.smart_reply import send_photo_message, smart_callback_reply
from presentation.bot.utils.telegram import (
    send_photo_to_thread,
    send_to_thread,
    send_video_to_thread,
)

from aiogram.types import FSInputFile


LETTER_TO_IDX = {"A": 0, "B": 1, "C": 2, "D": 3}


def _format_question(phrase: str, options: list, template: str) -> str:
    """Форматирует вопрос с вариантами A/B/C/D."""
    return template.format(
        phrase=phrase,
        opt_a=options[0] if len(options) > 0 else "",
        opt_b=options[1] if len(options) > 1 else "",
        opt_c=options[2] if len(options) > 2 else "",
        opt_d=options[3] if len(options) > 3 else "",
    )


async def _send_question(
    bot,
    chat_id: int,
    text: str,
    thread_id: int | None,
    reply_markup,
    media_file: str | None,
    media_type: str | None,
    user_id: int,
    game_type: str,
) -> None:
    """
    Отправить вопрос игры (с фото/видео если media указано, иначе текстом).

    Кэширует file_id медиа после первой отправки.
    """
    # Без медиа — обычный текст
    if not media_file or not media_type:
        await send_to_thread(
            bot, chat_id, text, thread_id,
            reply_markup=reply_markup,
            user_id=user_id,
            game_type=game_type,
        )
        return

    # С медиа — фото или видео
    media = await get_game_media(media_file)
    if media is None:
        # Fallback: файл не найден, отправляем только текст
        await send_to_thread(
            bot, chat_id, text, thread_id,
            reply_markup=reply_markup,
            user_id=user_id,
            game_type=game_type,
        )
        return

    if media_type == "photo":
        sent = await send_photo_to_thread(
            bot, chat_id, media,
            caption=text,
            thread_id=thread_id,
            reply_markup=reply_markup,
        )
        if sent and sent.photo and isinstance(media, FSInputFile):
            await cache_game_media(media_file, media, sent.photo[-1].file_id)
    elif media_type == "video":
        sent = await send_video_to_thread(
            bot, chat_id, media,
            caption=text,
            thread_id=thread_id,
            reply_markup=reply_markup,
        )
        if sent and sent.video and isinstance(media, FSInputFile):
            await cache_game_media(media_file, media, sent.video.file_id)
    else:
        # Неизвестный тип — fallback на текст
        await send_to_thread(
            bot, chat_id, text, thread_id,
            reply_markup=reply_markup,
            user_id=user_id,
            game_type=game_type,
        )


# ==============================
# [MESSAGE][GAMES] Кнопка Игры из reply keyboard
# ==============================
async def process_games_menu(
    message: Message,
    state: FSMContext,
    user: User,
) -> None:
    """Показ меню игр."""
    await state.clear()

    await send_photo_message(
        message,
        text=messages.GAMES_MENU,
        photo_key="games_mascot",
        reply_markup=GamesBuilder.menu_keyboard(page=0),
    )


# ==============================
# [CALLBACK][GAMES] Меню игр (пагинация)
# ==============================
async def process_games_callback(
    callback: CallbackQuery,
    callback_data: GamesMenuCallback,
    state: FSMContext,
    user: User,
    **kwargs,
) -> None:
    """Показ меню игр по callback."""
    await state.clear()

    await smart_callback_reply(
        callback,
        text=messages.GAMES_MENU,
        reply_markup=GamesBuilder.menu_keyboard(page=callback_data.page),
        photo_key="games_mascot",
    )


# ==============================
# [CALLBACK][GAMES] Выбор конкретной игры — стартовое сообщение
# ==============================
async def process_game_select(
    callback: CallbackQuery,
    callback_data: GameSelectCallback,
    state: FSMContext,
    user: User,
) -> None:
    """Показ стартового сообщения игры."""
    game: str = callback_data.game
    source: str = callback_data.source

    # Карточки — заглушка
    if game == "cards":
        await smart_callback_reply(
            callback,
            text=messages.GAMES_CARDS_STUB,
            reply_markup=GamesBuilder.cards_stub_keyboard(source),
        )
        return

    # Идиомус — стартовое сообщение с картинкой
    if game == "idioms":
        await smart_callback_reply(
            callback,
            text=messages.IDIOM_START,
            photo_key="idiom_start",
            reply_markup=GamesBuilder.idiom_start_keyboard(source),
        )
        return

    # Грамматикус — стартовое сообщение с картинкой
    if game == "grammar":
        await smart_callback_reply(
            callback,
            text=messages.GRAMMAR_START,
            photo_key="grammar_start",
            reply_markup=GamesBuilder.grammar_start_keyboard(source),
        )
        return


# ==============================
# [CALLBACK] Кнопка "Начать" в стартовом сообщении
# ==============================
async def process_game_start(
    callback: CallbackQuery,
    callback_data: GameStartCallback,
    state: FSMContext,
    user: User,
) -> None:
    """Обработка кнопки Начать."""
    game: str = callback_data.game
    source: str = callback_data.source

    # Идиомус — получаем топик и начинаем
    if game == "idioms":
        idiom_service = get_idiom_service()
        idioms = await idiom_service.get_random_idioms(10)

        if not idioms:
            await callback.message.answer(
                text="📭 Пока нет доступных вопросов для Идиомуса",
                reply_markup=GamesBuilder.back_keyboard(source),
            )
            return

        # Получаем/создаём топик
        thread_service = get_game_thread_service()
        thread_id = await thread_service.get_or_create_thread(
            bot=callback.bot,
            chat_id=callback.message.chat.id,
            user_id=user.telegram_id,
            game_type="idioms",
        )

        await state.set_state(IdiomTestState.awaiting_answer)
        await state.update_data(
            idioms=[i.model_dump() for i in idioms],
            current=0,
            score=0,
            source=source,
            thread_id=thread_id,
        )

        idiom = idioms[0]
        text = _format_question(idiom.phrase, idiom.options, messages.IDIOM_QUESTION)

        await _send_question(
            bot=callback.bot,
            chat_id=callback.message.chat.id,
            text=text,
            thread_id=thread_id,
            reply_markup=GamesBuilder.question_inline_keyboard("idioms"),
            media_file=idiom.media_file,
            media_type=idiom.media_type,
            user_id=user.telegram_id,
            game_type="idioms",
        )
        return

    # Грамматикус — показываем выбор уровня
    if game == "grammar":
        await smart_callback_reply(
            callback,
            text=messages.GRAMMAR_LEVEL_SELECT,
            reply_markup=GamesBuilder.grammar_level_keyboard(source),
        )
        return


# ==============================
# [CALLBACK] Выбор уровня Грамматикуса
# ==============================
async def process_grammar_level(
    callback: CallbackQuery,
    callback_data: GrammarLevelCallback,
    state: FSMContext,
    user: User,
) -> None:
    """Запуск Грамматикуса с выбранным уровнем."""
    level: str = callback_data.level
    source: str = callback_data.source

    service = get_grammar_question_service()
    questions = await service.get_random_questions(10, level=level)

    if not questions:
        await callback.answer(
            text="📭 Пока нет доступных вопросов для этого уровня",
            show_alert=True
        )
        return

    # Получаем/создаём топик
    thread_service = get_game_thread_service()
    thread_id = await thread_service.get_or_create_thread(
        bot=callback.bot,
        chat_id=callback.message.chat.id,
        user_id=user.telegram_id,
        game_type="grammar",
    )

    await state.set_state(GrammarGameState.awaiting_answer)
    await state.update_data(
        questions=[q.model_dump() for q in questions],
        current=0,
        score=0,
        source=source,
        level=level,
        thread_id=thread_id,
    )

    question = questions[0]
    text = _format_question(question.phrase, question.options, messages.GRAMMAR_QUESTION)

    await _send_question(
        bot=callback.bot,
        chat_id=callback.message.chat.id,
        text=text,
        thread_id=thread_id,
        reply_markup=GamesBuilder.question_inline_keyboard("grammar"),
        media_file=question.media_file,
        media_type=question.media_type,
        user_id=user.telegram_id,
        game_type="grammar",
    )


# ==============================
# [CALLBACK] Ответ на вопрос через inline кнопки (A/B/C/D/skip)
# ==============================
async def process_game_answer(
    callback: CallbackQuery,
    callback_data: GameAnswerCallback,
    state: FSMContext,
    user: User,
) -> None:
    """Обработка ответа через inline кнопки в топике."""
    game: str = callback_data.game
    answer: str = callback_data.answer
    current_state = await state.get_state()

    await callback.message.edit_reply_markup(reply_markup=None)

    # Проверяем что мы в правильном состоянии (защита от двойного клика)
    if game == "idioms" and current_state != IdiomTestState.awaiting_answer:
        await callback.answer()
        return
    
    if game == "grammar" and current_state != GrammarGameState.awaiting_answer:
        await callback.answer()
        return

    data: dict = await state.get_data()
    thread_id = data.get("thread_id")
    source: str = data.get("source", "games")
    bot = callback.bot
    chat_id = callback.message.chat.id
    tid = user.telegram_id

    # Имитируем ответ пользователя в топике
    if answer == "skip":
        user_text = "👉 Пропустить"
    else:
        user_text = f"👉 {answer}"

    await send_to_thread(bot, chat_id, user_text, thread_id, user_id=tid, game_type=game)

    if game == "idioms":
        await _process_idiom_answer_inline(callback, state, data, answer, thread_id, source, user)
    elif game == "grammar":
        await _process_grammar_answer_inline(callback, state, data, answer, thread_id, source, user)


async def _process_idiom_answer_inline(
    callback: CallbackQuery,
    state: FSMContext,
    data: dict,
    answer: str,
    thread_id: int | None,
    source: str,
    user: User,
) -> None:
    """Обработка ответа Идиомуса (inline)."""
    idioms_data: list = data.get("idioms", [])
    score: int = data.get("score", 0)
    current: int = data.get("current", 0)
    total: int = len(idioms_data)
    bot = callback.bot
    chat_id = callback.message.chat.id
    tid = user.telegram_id
    _t = {"user_id": tid, "game_type": "idioms"}

    if current >= total:
        await state.clear()
        await callback.answer()
        return

    # Блокируем ввод
    await state.set_state(IdiomTestState.in_progress)
    await callback.answer()

    idiom = Idiom(**idioms_data[current])
    correct_idx: int = idiom.correct_index
    correct_letter: str = LETTERS[correct_idx] if correct_idx < len(LETTERS) else "?"
    a_idx: int = LETTER_TO_IDX.get(answer, -1)

    # Формируем ответ
    if a_idx == -1:
        text = messages.IDIOM_SKIP.format(
            correct_letter=correct_letter,
            phrase=idiom.phrase,
            correct_text=idiom.options[correct_idx],
            meaning=idiom.meaning,
        )
    elif a_idx == correct_idx:
        score += 1
        text = messages.IDIOM_CORRECT.format(
            correct_letter=correct_letter,
            phrase=idiom.phrase,
            correct_text=idiom.options[correct_idx],
            meaning=idiom.meaning,
        )
    else:
        user_letter: str = LETTERS[a_idx]
        text = messages.IDIOM_WRONG.format(
            correct_letter=correct_letter,
            user_letter=user_letter,
            phrase=idiom.phrase,
            correct_text=idiom.options[correct_idx],
            meaning=idiom.meaning,
        )

    next_idx: int = current + 1
    await state.update_data(score=score, current=next_idx)

    await send_to_thread(bot, chat_id, text, thread_id, **_t)

    if next_idx < total:
        next_idiom = Idiom(**idioms_data[next_idx])
        q_text = _format_question(next_idiom.phrase, next_idiom.options, messages.IDIOM_QUESTION)

        await state.set_state(IdiomTestState.awaiting_answer)

        await _send_question(
            bot=bot,
            chat_id=chat_id,
            text=q_text,
            thread_id=thread_id,
            reply_markup=GamesBuilder.question_inline_keyboard("idioms"),
            media_file=next_idiom.media_file,
            media_type=next_idiom.media_type,
            user_id=tid,
            game_type="idioms",
        )
    else:
        percentage: int = round(score / total * 100) if total > 0 else 0

        if percentage < 40:
            verdict = messages.IDIOM_VERDICT_LOW
            title = messages.IDIOM_RESULT_TITLE_LOW
        elif percentage < 75:
            verdict = messages.IDIOM_VERDICT_MID
            title = messages.IDIOM_RESULT_TITLE_MID
        else:
            verdict = messages.IDIOM_VERDICT_HIGH
            title = messages.IDIOM_RESULT_TITLE_HIGH

        test_service = get_test_service()
        await test_service.save_result(user.id, "idioms", score, total)

        await state.clear()

        await send_to_thread(
            bot, chat_id,
            messages.IDIOM_RESULT.format(
                title=title, score=score, total=total, verdict=verdict,
            ),
            thread_id,
            reply_markup=GamesBuilder.idiom_result_keyboard(),
            **_t,
        )

        await send_to_thread(
            bot, chat_id, "👇", thread_id,
            reply_markup=GamesBuilder.result_inline_keyboard(source),
            **_t,
        )


async def _process_grammar_answer_inline(
    callback: CallbackQuery,
    state: FSMContext,
    data: dict,
    answer: str,
    thread_id: int | None,
    source: str,
    user: User,
) -> None:
    """Обработка ответа Грамматикуса (inline)."""
    questions_data: list = data.get("questions", [])
    score: int = data.get("score", 0)
    current: int = data.get("current", 0)
    total: int = len(questions_data)
    bot = callback.bot
    chat_id = callback.message.chat.id
    tid = user.telegram_id
    _t = {"user_id": tid, "game_type": "grammar"}

    if current >= total:
        await state.clear()
        await callback.answer()
        return

    # Блокируем ввод
    await state.set_state(GrammarGameState.in_progress)
    await callback.answer()

    question = GrammarQuestion(**questions_data[current])
    correct_idx: int = question.correct_index
    correct_letter: str = LETTERS[correct_idx] if correct_idx < len(LETTERS) else "?"
    explanation: str = question.explanation or ""
    a_idx: int = LETTER_TO_IDX.get(answer, -1)

    # Формируем ответ
    if a_idx == -1:
        text = messages.GRAMMAR_SKIP.format(
            correct_letter=correct_letter,
            explanation=explanation,
        )
    elif a_idx == correct_idx:
        score += 1
        text = messages.GRAMMAR_CORRECT.format(
            correct_letter=correct_letter,
            explanation=explanation,
        )
    else:
        user_letter: str = LETTERS[a_idx]
        text = messages.GRAMMAR_WRONG.format(
            correct_letter=correct_letter,
            user_letter=user_letter,
            explanation=explanation,
        )

    next_idx: int = current + 1
    await state.update_data(score=score, current=next_idx)

    await send_to_thread(bot, chat_id, text, thread_id, **_t)

    if next_idx < total:
        next_q = GrammarQuestion(**questions_data[next_idx])
        q_text = _format_question(next_q.phrase, next_q.options, messages.GRAMMAR_QUESTION)

        await state.set_state(GrammarGameState.awaiting_answer)

        await _send_question(
            bot=bot,
            chat_id=chat_id,
            text=q_text,
            thread_id=thread_id,
            reply_markup=GamesBuilder.question_inline_keyboard("grammar"),
            media_file=next_q.media_file,
            media_type=next_q.media_type,
            user_id=tid,
            game_type="grammar",
        )
    else:
        percentage: int = round(score / total * 100) if total > 0 else 0

        if percentage < 40:
            verdict = messages.GRAMMAR_VERDICT_LOW
            title = messages.GRAMMAR_RESULT_TITLE_LOW
        elif percentage < 75:
            verdict = messages.GRAMMAR_VERDICT_MID
            title = messages.GRAMMAR_RESULT_TITLE_MID
        else:
            verdict = messages.GRAMMAR_VERDICT_HIGH
            title = messages.GRAMMAR_RESULT_TITLE_HIGH

        await state.clear()

        await send_to_thread(
            bot, chat_id,
            messages.GRAMMAR_RESULT.format(
                title=title, score=score, total=total, verdict=verdict,
            ),
            thread_id,
            reply_markup=GamesBuilder.grammar_result_keyboard(),
            **_t,
        )

        await send_to_thread(
            bot, chat_id, "👇", thread_id,
            reply_markup=GamesBuilder.result_inline_keyboard(source),
            **_t,
        )


def register_games_handlers(dp: Dispatcher) -> None:
    """Регистрация хендлеров игр."""

    # Reply keyboard кнопки Игры
    dp.message.register(
        process_games_menu,
        F.text.contains("Игры"),
    )

    # Inline: меню игр
    dp.callback_query.register(
        process_games_callback,
        GamesMenuCallback.filter(),
    )

    # Inline: выбор игры (стартовое сообщение)
    dp.callback_query.register(
        process_game_select,
        GameSelectCallback.filter(),
    )

    # Inline: кнопка Начать
    dp.callback_query.register(
        process_game_start,
        GameStartCallback.filter(),
    )

    # Inline: выбор уровня Грамматикуса
    dp.callback_query.register(
        process_grammar_level,
        GrammarLevelCallback.filter(),
    )

    # Inline: ответ на вопрос (A/B/C/D/skip)
    dp.callback_query.register(
        process_game_answer,
        GameAnswerCallback.filter(),
    )
