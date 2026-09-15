package com.uwords.e2e.tests.auth;

import com.uwords.e2e.AbstractUiTest;
import com.uwords.e2e.Description;
import com.uwords.e2e.statements.auth.AuthStubStatements;
import com.uwords.e2e.statements.auth.EmailCodeEntryStatements;
import java.time.Instant;
import java.util.List;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

@DisplayName("UI Test Scenario 1.1: Пользователь открывает приложение, получает код на почту и оказывается внутри")
public class EmailCodeEntryTest extends AbstractUiTest {

    private final EmailCodeEntryStatements emailCodeEntry = new EmailCodeEntryStatements();
    private final AuthStubStatements authStub = new AuthStubStatements();

    @Test
    @Description("""
        UI Test Scenario 1.1: Пользователь открывает приложение, получает код на почту и оказывается внутри
        Дано пользователь открывает приложение
        Тогда виден экран почты с нейтральным заголовком «Войти или создать аккаунт»
        И поле адреса пустое и в фокусе
        И кнопка «Получить код» недоступна
        И ячеек кода, отсчёта и кнопки «Отправить новый код» на экране нет
        """)
    void should_show_email_screen_on_open() {
        emailCodeEntry.navigateToEmailScreen(webDriver, appUrl);

        emailCodeEntry.assertEmailScreenIsDisplayed(webDriver, wait);
        emailCodeEntry.assertEmailInputIsEmptyAndFocused(webDriver, wait);
        emailCodeEntry.assertRequestCodeButtonIsDisabled(webDriver, wait);
        emailCodeEntry.assertCodeElementsAreAbsent(webDriver);
    }

    @Test
    @Description("""
        UI Test Scenario 1.1: Пользователь открывает приложение, получает код на почту и оказывается внутри
        Дано пользователь открыл приложение и видит экран почты
        Когда он вводит свой адрес и нажимает «Получить код»
        Тогда сервису ушёл ровно один запрос кода на этот адрес
        И виден экран кода с этим адресом
        И идёт обратный отсчёт от срока, который назвал сервис
        И шесть ячеек кода пусты и первая в фокусе
        И кнопка «Подтвердить» недоступна
        И кнопка «Отправить новый код» и ссылка «Изменить адрес» доступны
        """)
    void should_request_code_and_show_code_screen() {
        String email = authStub.uniqueEmail();
        emailCodeEntry.navigateToEmailScreen(webDriver, appUrl);

        emailCodeEntry.enterEmail(webDriver, wait, email);
        emailCodeEntry.clickRequestCode(webDriver, wait);

        emailCodeEntry.assertCodeScreenIsDisplayedFor(webDriver, wait, email);
        authStub.assertExactlyOneStartRequest(email);
        Instant serviceExpiresAt = authStub.issuedExpiresAt(email);
        emailCodeEntry.assertCountdownIsRunningFrom(webDriver, wait, serviceExpiresAt);
        emailCodeEntry.assertCodeCellsAreEmptyAndFirstFocused(webDriver, wait);
        emailCodeEntry.assertConfirmButtonIsDisabled(webDriver, wait);
        emailCodeEntry.assertResendAndChangeEmailAreAvailable(webDriver, wait);
    }

    @Test
    @Description("""
        UI Test Scenario 1.1: Пользователь открывает приложение, получает код на почту и оказывается внутри
        Дано пользователь ввёл свой адрес, запросил код и видит экран кода
        Когда он вводит код, который сервис отправил на его адрес, и нажимает «Подтвердить»
        Тогда сервису ушёл ровно один запрос проверки с выданным ему идентификатором и кодом как строкой
        И виден экран «вошёл»
        И на экране нет ни токенов, ни идентификатора сессии, ни идентификатора запроса кода
        """)
    void should_confirm_code_and_sign_in() {
        String email = authStub.uniqueEmail();
        emailCodeEntry.openCodeScreenFor(webDriver, wait, appUrl, email);
        String code = authStub.codeSentTo(email);

        emailCodeEntry.enterCode(webDriver, wait, code);
        emailCodeEntry.clickConfirm(webDriver, wait);

        emailCodeEntry.assertSignedInScreenIsDisplayed(webDriver, wait);
        authStub.assertExactlyOneVerifyRequest(email);
        List<String> secrets = authStub.issuedSecrets(email);
        emailCodeEntry.assertScreenShowsNoneOf(webDriver, secrets);
    }
}
