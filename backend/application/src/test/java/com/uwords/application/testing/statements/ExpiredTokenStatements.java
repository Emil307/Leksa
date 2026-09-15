package com.uwords.application.testing.statements;

import static com.uwords.application.testing.statements.ApplicationBootData.AUTHORIZATION_HEADER;
import static com.uwords.application.testing.statements.ApplicationBootData.PROFILE_PATH;
import static com.uwords.application.testing.statements.ApplicationBootData.UNAUTHORIZED_BODY;
import static com.uwords.application.testing.statements.ApplicationBootData.expiredBearerHeader;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.content;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.ResultActions;

public class ExpiredTokenStatements {

    private static final int UNAUTHORIZED_STATUS = 401;

    private final MockMvc mockMvc;

    private String header;
    private ResultActions response;

    public ExpiredTokenStatements(MockMvc mockMvc) {
        this.mockMvc = mockMvc;
    }

    public void givenAnExpiredButCorrectlySignedToken() {
        header = expiredBearerHeader();
    }

    public void whenTheProfileIsRequested() throws Exception {
        response = mockMvc.perform(get(PROFILE_PATH).header(AUTHORIZATION_HEADER, header));
    }

    public void assertTheWiredClockRefusedTheRequestWithTheUniform401() throws Exception {
        response.andExpect(status().is(UNAUTHORIZED_STATUS))
                .andExpect(content().json(UNAUTHORIZED_BODY, true));
    }
}
