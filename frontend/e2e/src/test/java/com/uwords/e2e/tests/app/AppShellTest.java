package com.uwords.e2e.tests.app;

import com.uwords.e2e.AbstractUiTest;
import com.uwords.e2e.Description;
import com.uwords.e2e.statements.app.AppShellStatements;
import org.junit.jupiter.api.Test;

public class AppShellTest extends AbstractUiTest {

    private final AppShellStatements appShell = new AppShellStatements();

    @Test
    @Description("""
        UI Test Scenario 0: Оболочка приложения открывается
        Дано пользователь открывает корневой адрес приложения
        Тогда отображается оболочка приложения
        И отображается непустой заголовок приложения
        """)
    void should_display_app_shell_at_root() {
        appShell.navigateToApp(webDriver, appUrl);

        appShell.assertAppShellIsDisplayed(webDriver, wait);
        appShell.assertAppTitleIsDisplayed(webDriver, wait);
    }
}
