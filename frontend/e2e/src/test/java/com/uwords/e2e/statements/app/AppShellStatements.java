package com.uwords.e2e.statements.app;

import static org.assertj.core.api.Assertions.assertThat;

import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;

public class AppShellStatements {

    private static final By APP_ROOT = By.cssSelector("[data-testid='app-root']");
    private static final By APP_TITLE = By.cssSelector("[data-testid='app-title']");

    public void navigateToApp(WebDriver driver, String appUrl) {
        driver.get(appUrl);
    }

    public void assertAppShellIsDisplayed(WebDriver driver, WebDriverWait wait) {
        WebElement root = wait.until(ExpectedConditions.visibilityOfElementLocated(APP_ROOT));
        assertThat(root.isDisplayed()).as("app shell is displayed").isTrue();
    }

    public void assertAppTitleIsDisplayed(WebDriver driver, WebDriverWait wait) {
        WebElement title = wait.until(ExpectedConditions.visibilityOfElementLocated(APP_TITLE));
        assertThat(title.isDisplayed()).as("app title is displayed").isTrue();
        assertThat(title.getText()).as("app title text").isNotBlank();
    }
}
