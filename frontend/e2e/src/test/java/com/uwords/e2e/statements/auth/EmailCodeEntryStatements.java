package com.uwords.e2e.statements.auth;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.within;

import java.time.Duration;
import java.time.Instant;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;

public class EmailCodeEntryStatements {

    private static final By APP_ROOT = By.cssSelector("[data-testid='app-root']");
    private static final By EMAIL_SCREEN = By.cssSelector("[data-testid='email-screen']");
    private static final By EMAIL_TITLE = By.cssSelector("[data-testid='email-title']");
    private static final By EMAIL_INPUT = By.cssSelector("[data-testid='email-input']");
    private static final By REQUEST_CODE_BUTTON = By.cssSelector("[data-testid='request-code-button']");
    private static final By CODE_SCREEN = By.cssSelector("[data-testid='code-screen']");
    private static final By CODE_EMAIL = By.cssSelector("[data-testid='code-email']");
    private static final By CODE_COUNTDOWN = By.cssSelector("[data-testid='code-countdown']");
    private static final By CODE_CELLS = By.cssSelector("[data-testid^='code-cell-']");
    private static final By CODE_CELL_FIRST = By.cssSelector("[data-testid='code-cell-0']");
    private static final By CONFIRM_BUTTON = By.cssSelector("[data-testid='confirm-button']");
    private static final By RESEND_BUTTON = By.cssSelector("[data-testid='resend-button']");
    private static final By CHANGE_EMAIL_LINK = By.cssSelector("[data-testid='change-email-link']");
    private static final By SIGNED_IN_SCREEN = By.cssSelector("[data-testid='signed-in-screen']");
    private static final By SIGNED_IN_TITLE = By.cssSelector("[data-testid='signed-in-title']");
    private static final int CODE_LENGTH = 6;
    private static final int COUNTDOWN_TOLERANCE_SECONDS = 3;
    private static final Pattern COUNTDOWN_FORMAT = Pattern.compile("(\\d):([0-5]\\d)");
    private static final String EMAIL_SCREEN_TITLE = "Войти или создать аккаунт";
    private static final String REQUEST_CODE_LABEL = "Получить код";
    private static final String CONFIRM_LABEL = "Подтвердить";
    private static final String RESEND_LABEL = "Отправить новый код";
    private static final String CHANGE_EMAIL_LABEL = "Изменить адрес";
    private static final String SIGNED_IN_TITLE_TEXT = "Вы вошли";

    public void navigateToEmailScreen(WebDriver driver, String appUrl) {
        driver.get(appUrl);
    }

    public void openCodeScreenFor(WebDriver driver, WebDriverWait wait, String appUrl, String email) {
        navigateToEmailScreen(driver, appUrl);
        enterEmail(driver, wait, email);
        clickRequestCode(driver, wait);
        wait.until(ExpectedConditions.visibilityOfElementLocated(CODE_SCREEN));
    }

    public void enterEmail(WebDriver driver, WebDriverWait wait, String email) {
        wait.until(ExpectedConditions.visibilityOfElementLocated(EMAIL_INPUT)).sendKeys(email);
    }

    public void clickRequestCode(WebDriver driver, WebDriverWait wait) {
        wait.until(ExpectedConditions.elementToBeClickable(REQUEST_CODE_BUTTON)).click();
    }

    public void enterCode(WebDriver driver, WebDriverWait wait, String code) {
        wait.until(ExpectedConditions.visibilityOfElementLocated(CODE_CELL_FIRST));
        for (int i = 0; i < CODE_LENGTH; i++) {
            driver.findElement(codeCell(i)).sendKeys(String.valueOf(code.charAt(i)));
        }
    }

    public void clickConfirm(WebDriver driver, WebDriverWait wait) {
        wait.until(ExpectedConditions.elementToBeClickable(CONFIRM_BUTTON)).click();
    }

    public void assertEmailScreenIsDisplayed(WebDriver driver, WebDriverWait wait) {
        WebElement screen = wait.until(ExpectedConditions.visibilityOfElementLocated(EMAIL_SCREEN));
        assertThat(screen.isDisplayed()).as("email screen is displayed").isTrue();
        WebElement title = driver.findElement(EMAIL_TITLE);
        assertThat(title.isDisplayed()).as("email title is displayed").isTrue();
        assertThat(title.getText()).as("email title text").isEqualTo(EMAIL_SCREEN_TITLE);
    }

    public void assertEmailInputIsEmptyAndFocused(WebDriver driver, WebDriverWait wait) {
        WebElement input = wait.until(ExpectedConditions.visibilityOfElementLocated(EMAIL_INPUT));
        assertThat(input.isDisplayed()).as("email input is displayed").isTrue();
        assertThat(input.getDomProperty("value")).as("email input value").isEmpty();
        assertThat(driver.switchTo().activeElement()).as("email input is focused").isEqualTo(input);
    }

    public void assertRequestCodeButtonIsDisabled(WebDriver driver, WebDriverWait wait) {
        WebElement button = wait.until(ExpectedConditions.visibilityOfElementLocated(REQUEST_CODE_BUTTON));
        assertThat(button.isDisplayed()).as("request code button is displayed").isTrue();
        assertThat(button.getText()).as("request code button label").isEqualTo(REQUEST_CODE_LABEL);
        assertThat(button.isEnabled()).as("request code button is enabled").isFalse();
    }

    public void assertCodeElementsAreAbsent(WebDriver driver) {
        assertThat(driver.findElements(CODE_CELLS)).as("code cells on email screen").isEmpty();
        assertThat(driver.findElements(CODE_COUNTDOWN)).as("countdown on email screen").isEmpty();
        assertThat(driver.findElements(RESEND_BUTTON)).as("resend button on email screen").isEmpty();
    }

    public void assertCodeScreenIsDisplayedFor(WebDriver driver, WebDriverWait wait, String email) {
        WebElement screen = wait.until(ExpectedConditions.visibilityOfElementLocated(CODE_SCREEN));
        assertThat(screen.isDisplayed()).as("code screen is displayed").isTrue();
        WebElement shownEmail = driver.findElement(CODE_EMAIL);
        assertThat(shownEmail.isDisplayed()).as("code screen email is displayed").isTrue();
        assertThat(shownEmail.getText()).as("code screen email").isEqualTo(email);
    }

    public void assertCountdownIsRunningFrom(WebDriver driver, WebDriverWait wait, Instant serviceExpiresAt) {
        WebElement countdown = wait.until(ExpectedConditions.visibilityOfElementLocated(CODE_COUNTDOWN));
        assertThat(countdown.isDisplayed()).as("countdown is displayed").isTrue();
        String first = countdown.getText();
        long remaining = Duration.between(Instant.now(), serviceExpiresAt).toSeconds();
        assertThat(countdownSeconds(first)).as("countdown seconds until service expiry")
                .isCloseTo(remaining, within((long) COUNTDOWN_TOLERANCE_SECONDS));
        wait.until(ExpectedConditions.not(ExpectedConditions.textToBe(CODE_COUNTDOWN, first)));
        assertThat(countdownSeconds(countdown.getText())).as("countdown ticks down by one second")
                .isEqualTo(countdownSeconds(first) - 1);
    }

    public void assertCodeCellsAreEmptyAndFirstFocused(WebDriver driver, WebDriverWait wait) {
        WebElement first = wait.until(ExpectedConditions.visibilityOfElementLocated(CODE_CELL_FIRST));
        List<WebElement> cells = driver.findElements(CODE_CELLS);
        assertThat(cells).as("six code cells").hasSize(CODE_LENGTH);
        assertThat(cells).extracting(WebElement::isDisplayed).as("code cells are displayed")
                .containsExactly(true, true, true, true, true, true);
        assertThat(cells).extracting(cell -> cell.getDomProperty("value")).as("code cells are empty")
                .containsExactly("", "", "", "", "", "");
        assertThat(driver.switchTo().activeElement()).as("first code cell is focused").isEqualTo(first);
    }

    public void assertConfirmButtonIsDisabled(WebDriver driver, WebDriverWait wait) {
        WebElement button = wait.until(ExpectedConditions.visibilityOfElementLocated(CONFIRM_BUTTON));
        assertThat(button.isDisplayed()).as("confirm button is displayed").isTrue();
        assertThat(button.getText()).as("confirm button label").isEqualTo(CONFIRM_LABEL);
        assertThat(button.isEnabled()).as("confirm button is enabled").isFalse();
    }

    public void assertResendAndChangeEmailAreAvailable(WebDriver driver, WebDriverWait wait) {
        WebElement resend = wait.until(ExpectedConditions.visibilityOfElementLocated(RESEND_BUTTON));
        assertThat(resend.isDisplayed()).as("resend button is displayed").isTrue();
        assertThat(resend.getText()).as("resend button label").isEqualTo(RESEND_LABEL);
        assertThat(resend.isEnabled()).as("resend button is enabled").isTrue();
        WebElement change = driver.findElement(CHANGE_EMAIL_LINK);
        assertThat(change.isDisplayed()).as("change email link is displayed").isTrue();
        assertThat(change.getText()).as("change email link label").isEqualTo(CHANGE_EMAIL_LABEL);
        assertThat(change.isEnabled()).as("change email link is enabled").isTrue();
    }

    public void assertSignedInScreenIsDisplayed(WebDriver driver, WebDriverWait wait) {
        WebElement screen = wait.until(ExpectedConditions.visibilityOfElementLocated(SIGNED_IN_SCREEN));
        assertThat(screen.isDisplayed()).as("signed-in screen is displayed").isTrue();
        WebElement title = driver.findElement(SIGNED_IN_TITLE);
        assertThat(title.isDisplayed()).as("signed-in title is displayed").isTrue();
        assertThat(title.getText()).as("signed-in title text").isEqualTo(SIGNED_IN_TITLE_TEXT);
    }

    public void assertScreenShowsNoneOf(WebDriver driver, List<String> secrets) {
        String screenText = driver.findElement(APP_ROOT).getText();
        assertThat(screenText).as("screen text must not reveal issued secrets").doesNotContain(secrets);
    }

    private static By codeCell(int index) {
        return By.cssSelector("[data-testid='code-cell-" + index + "']");
    }

    private static long countdownSeconds(String text) {
        Matcher matcher = COUNTDOWN_FORMAT.matcher(text);
        assertThat(matcher.matches()).as("countdown %s has m:ss format", text).isTrue();
        return Long.parseLong(matcher.group(1)) * 60 + Long.parseLong(matcher.group(2));
    }
}
