package com.uwords.e2e;

import java.time.Duration;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;
import org.openqa.selenium.support.ui.WebDriverWait;

public abstract class AbstractUiTest {

    private static final Duration WAIT_TIMEOUT = Duration.ofSeconds(10);
    private static final boolean CLOSE_BROWSER_AFTER_TEST = true;

    protected WebDriver webDriver;
    protected WebDriverWait wait;
    protected String appUrl;

    @BeforeEach
    void openBrowser() {
        appUrl = requireAppUrl();
        webDriver = new ChromeDriver(chromeOptions());
        wait = new WebDriverWait(webDriver, WAIT_TIMEOUT);
    }

    @AfterEach
    void closeBrowser() {
        if (CLOSE_BROWSER_AFTER_TEST && webDriver != null) {
            webDriver.quit();
        }
    }

    private static String requireAppUrl() {
        String url = System.getenv("APP_URL");
        if (url == null || url.isBlank()) {
            throw new IllegalStateException("APP_URL is required; run via frontend/infrastructure/scripts/test-e2e.sh");
        }
        return url;
    }

    private static ChromeOptions chromeOptions() {
        ChromeOptions options = new ChromeOptions();
        if (!"false".equalsIgnoreCase(System.getenv("E2E_HEADLESS"))) {
            options.addArguments("--headless=new");
        }
        options.addArguments("--window-size=1920,1080");
        options.addArguments("--disable-gpu");
        options.addArguments("--no-sandbox");
        return options;
    }
}
