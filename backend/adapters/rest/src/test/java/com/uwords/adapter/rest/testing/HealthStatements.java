package com.uwords.adapter.rest.testing;

import com.uwords.adapter.rest.controller.HealthController;
import com.uwords.usecase.service.HealthService;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.ResultActions;
import org.springframework.test.web.servlet.request.MockMvcRequestBuilders;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;

import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.content;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

public class HealthStatements {

    private static final String HEALTH_PATH = "/health";
    private static final String UP_BODY = """
            {"status":"UP","database":"UP"}""";
    private static final String DOWN_BODY = """
            {"status":"DOWN","database":"DOWN"}""";

    private final HealthService service = mock(HealthService.class);

    private ResultActions response;

    public void givenTheApplicationIsReady() {
        when(service.isReady()).thenReturn(true);
    }

    public void givenTheApplicationIsNotReady() {
        when(service.isReady()).thenReturn(false);
    }

    public void whenHealthIsRequested() throws Exception {
        MockMvc mockMvc = MockMvcBuilders.standaloneSetup(new HealthController(service)).build();
        response = mockMvc.perform(MockMvcRequestBuilders.get(HEALTH_PATH));
    }

    public void assertAnsweredUpWith200() throws Exception {
        response.andExpect(status().isOk()).andExpect(content().json(UP_BODY, true));
    }

    public void assertAnsweredDownWith503() throws Exception {
        response.andExpect(status().isServiceUnavailable()).andExpect(content().json(DOWN_BODY, true));
    }
}
