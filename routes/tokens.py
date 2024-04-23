"""Tokens route module."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import telebot  # type: ignore[import-untyped]

if TYPE_CHECKING:
    from logging import Logger

    from data.user_database import UserDatabase


class TokensRoute:
    """Route handling user requests related to tokens."""

    def __init__(  # type: ignore[no-any-unimported]
        self: TokensRoute,
        bot: telebot.TeleBot,
        logger: Logger,
        user_database: UserDatabase,
        provider_token: str,
    ) -> None:
        """Create TokensRoute.

        Args:
        ----
            bot (telebot.TeleBot): The telebot instance.
            logger (CustomLogger): The logger instance.
            user_database (UserDatabase): The user database instance.
            provider_token (str): The provider token.

        """
        self.bot = bot
        self.logger = logger
        self.database = user_database
        self.provider_token = provider_token
        self.register_callbacks()

        @bot.message_handler(commands=["tokens"])
        def tokens(message: telebot.types.Message) -> None:  # type: ignore[no-any-unimported]
            """Tokens command.

            Args:
            ----
                message (telebot.types.Message): The message object received from the user.

            Returns:
            -------
                None

            """  # noqa: E501
            self.__tokens(message)

        @bot.message_handler(content_types=["successful_payment"])
        def successful_payment(message: telebot.types.Message) -> None:  # type: ignore[no-any-unimported]
            """Successful payment callback.

            Args:
            ----
                message (telebot.types.Message): The message object received from the user.

            Returns:
            -------
                None

            """  # noqa: E501
            self.__successful_payment(message)

        @bot.pre_checkout_query_handler(func=lambda _: True)
        def pre_checkout(pre_checkout_query: telebot.types.PreCheckoutQuery) -> None:  # type: ignore[no-any-unimported]
            """Pre-checkout callback.

            pre_checkout_query (types.PreCheckoutQuery): The pre-checkout query object.
            """
            bot.answer_pre_checkout_query(
                pre_checkout_query.id,
                ok=True,
                error_message="Произошла ошибка. Попробуйте ещё раз позже.",
            )

        @bot.shipping_query_handler(func=lambda _: True)
        def shipping(shipping_query: telebot.types.ShippingQuery) -> None:  # type: ignore[no-any-unimported]
            """Shipping callback.

            shipping_query (types.ShippingQuery): The shipping query object.
            """
            bot.answer_shipping_query(
                shipping_query.id,
                ok=True,
                error_message="Произошла ошибка. Попробуйте ещё раз позже.",
            )

        self.logger.info("Tokens route initialized.", extra={"message_type": "server"})

    def __tokens(self: TokensRoute, message: telebot.types.Message) -> None:  # type: ignore[no-any-unimported]
        """Handle /tokens command.

        Args:
        ----
            message (telebot.types.Message): The message object received from the user.

        Returns:
        -------
            None

        """
        code, user = self.database.get_user(message.chat.id)
        ok_code = 200

        if code != ok_code:
            self.bot.send_message(
                message.chat.id,
                "Произошла ошибка. Попробуйте ещё раз позже.\nMы уже работаем над этим.",  # noqa: E501
            )

        if user is None:
            self.database.new_user(message.chat.id, message.from_user.username)
            self.bot.send_message(
                message.chat.id,
                f"Привет, {message.from_user.username}!\n"
                "---------------\n"
                "Ты не можешь получить токены, потому что ты не был зарегистрирован.\n"
                "Ho y меня хорошие новости! Я уже тебя зарагестрировал!\n"
                "Пришли мне голосовое сообщение/аудиофайл, и я помогу тебе создать конспект из него.\n"  # noqa: E501
                "---------------\n"
                "Посмотреть профиль /profile\n"
                "Получить токены /tokens\n"
                "Информация o боте /about\n"
                "Посмотреть цены /prices\n"
                "---------------",
            )
            return

        button1 = telebot.types.InlineKeyboardButton(
            "💸 20 токенов = 60₽",
            callback_data="0",
        )
        button2 = telebot.types.InlineKeyboardButton(
            "💸 50 токенов = 150₽",
            callback_data="1",
        )
        button3 = telebot.types.InlineKeyboardButton(
            "💸 100 токенов = 290₽ (-3%)",
            callback_data="2",
        )
        button4 = telebot.types.InlineKeyboardButton(
            "💸 300 токенов = 830₽ (-7%)",
            callback_data="3",
        )
        button5 = telebot.types.InlineKeyboardButton(
            "💸 1000 токенов = 2700₽ (-10%)",
            callback_data="4",
        )

        keyboard = telebot.types.InlineKeyboardMarkup(
            [[button1], [button2], [button3], [button4], [button5]],
        )

        self.bot.send_message(
            message.chat.id,
            "**Меню приобретения токенов.**\nГлaвнoe меню /start\nДocтyпныe покупки:",
            reply_markup=keyboard,
            parse_mode="Markdown",
        )

    def __successful_payment(self: TokensRoute, message: telebot.types.Message) -> None:  # type: ignore[no-any-unimported]
        """Handle successful payment callback.

        Args:
        ----
            message (telebot.types.Message): The message object received from the user.

        Returns:
        -------
            None

        """
        ind = int(message.successful_payment.invoice_payload)
        ok_code = 200

        _, amount, tokens = self.__get_price(ind)
        code = self.database.increase_tokens(message.chat.id, tokens)

        if code != ok_code:
            self.bot.send_message(
                message.chat.id,
                "Произошла ошибка. Попробуйте ещё раз позже.\nMы уже работаем над этим.",  # noqa: E501
            )
            return

        self.bot.send_message(
            message.chat.id,
            f"Ты купил {tokens} токенов за {amount // 100}₽\n"
            "---------------\n"
            "Пришли мне голосовое сообщение/аудиофайл, и я помогу тебе создать полноценный конспект из него!\n"  # noqa: E501
            "---------------\n"
            "Посмотреть профиль /profile\n"
            "Информация o боте /about\n"
            "Посмотреть цены /prices\n"
            "---------------",
        )

    def register_callbacks(self: TokensRoute) -> None:
        """Register callbacks for TokensRoute.

        Args:
        ----
            None

        Returns:
        -------
            None

        """

        @self.bot.callback_query_handler(func=lambda _: True)
        def payment_callbacks(call: telebot.types.CallbackQuery) -> None:  # type: ignore[no-any-unimported]
            """Payment callbacks.

            Args:
            ----
                call (telebot.types.CallbackQuery):
                    The callback query object received from the user.

            Returns:
            -------
                None

            """
            ind = int(call.data)
            text, amount, tokens = self.__get_price(ind)

            # Create receipt for payment
            receipt = {
                "items": [
                    {
                        "description": text,
                        "quantity": 1,
                        "amount": {
                            "value": str(amount // 100) + ".00",
                            "currency": "RUB",
                        },
                        "vat_code": 1,
                    },
                ],
            }
            receipt_to_json = f'{{"receipt": {json.dumps(receipt)}}}'

            # Send invoice
            self.bot.send_invoice(
                call.message.chat.id,
                title="Покупка токенов",
                description=text,
                invoice_payload=str(ind),
                provider_token=self.provider_token,
                currency="RUB",
                prices=[telebot.types.LabeledPrice(label=text, amount=amount)],
                need_email=True,
                send_email_to_provider=True,
                provider_data=receipt_to_json,
            )

    @staticmethod
    def __get_price(ind: int) -> [str, int, int]:
        prices = [
            ("💸 20 токенов", 6000, 20),
            ("💸 50 токенов", 15000, 50),
            ("💸 100 токенов (-3%)", 29000, 100),
            ("💸 300 токенов (-7%)", 83000, 300),
            ("💸 1000 токенов (-10%)", 270000, 1000),
        ]
        return prices[ind]
