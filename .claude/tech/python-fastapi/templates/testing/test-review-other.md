# Test Review Patterns: Other Layers (Python/FastAPI)

Python/pytest code examples for selenium, email, scheduling, and security test anti-patterns. For universal rules: `.claude/templates/testing/test-review-patterns.md`

## Selenium Anti-Pattern Examples

### BAD: Truthy check when the test controls the data
```python
assert date.text, "due date"
# GOOD: capture from API setup, assert the exact value
task = await task_statements.get_task(api_session)
assert date.text == task.due_date.strftime(DATE_FORMAT), "due date"
```

### BAD: In-app URL navigation
```python
def navigate_to_create_task_wizard(self, app_url):
    self.driver.get(f"{app_url}/create")
# GOOD: app root only, then click through the UI
def navigate_to_create_task_wizard(self, app_url):
    self.driver.get(app_url)
    self.driver.find_element(By.CSS_SELECTOR, '[data-testid="new-task-button"]').click()
```

### BAD: `NotImplementedError` in Statements
```python
def assert_error_banner_displayed(self):
    raise NotImplementedError()
# GOOD: Statements are functional in RED
def assert_error_banner_displayed(self):
    banner = self.driver.find_element(By.CSS_SELECTOR, '[data-testid="error-banner"]')
    assert banner.is_displayed(), "error banner is displayed"
    assert banner.text == "Something went wrong", "error banner message"
```

### BAD: Assertion shallower than the spec
```python
cards = self.driver.find_elements(By.CSS_SELECTOR, '[data-testid="task-card"]')
assert len(cards) >= 1, "task cards are displayed"
# GOOD: every sub-element the spec names gets its own locator and assertion
for card in cards:
    assert card.find_element(By.CSS_SELECTOR, '[data-testid="task-title"]').text, "card title"
    assert card.find_element(By.CSS_SELECTOR, '[data-testid="task-status"]').is_displayed(), "status badge"
    assert card.find_element(By.CSS_SELECTOR, '[data-testid="task-assignee"]').is_displayed(), "assignee"
    assert card.find_element(By.CSS_SELECTOR, '[data-testid="task-priority"]').text, "priority"
```

## Email Anti-Pattern Examples

### BAD: Only asserting that some mail was sent
```python
assert len(mail_outbox) == 1
# GOOD: recipient, subject and rendered body
message = mail_outbox[0]
assert message.recipient == "user@example.com", "recipient"
assert message.subject == "Reset your password", "subject"
assert RESET_TOKEN in message.html_body, "reset token rendered into the template"
```

### BAD: Substring check on the whole body when the value is deterministic
```python
assert "Reset" in message.html_body
# GOOD: assert the rendered placeholder, not the boilerplate
assert message.html_body == load_template("reset.html").replace("{token}", RESET_TOKEN)
```

## Scheduling Anti-Pattern Examples

### BAD: `asyncio.sleep` waiting for a job to fire
```python
await asyncio.sleep(3)
usecase.execute.assert_awaited()
# GOOD: poll the assertion with tenacity, and verify the arguments
@retry(stop=stop_after_delay(5), wait=wait_fixed(0.1))
async def assert_job_fired():
    usecase.execute.assert_awaited_once_with(EXPECTED_REQUEST)
```

### BAD: Business logic asserted at the scheduling layer
```python
assert (await repository.list_expired()) == []      # that is a usecase test
# GOOD: scheduling tests verify wiring only — the job delegates to the usecase
usecase.execute.assert_awaited_once()
```

## Security Anti-Pattern Examples

### BAD: Token assertion that never decodes the token
```python
assert token is not None
# GOOD: decode and assert the claims
claims = jwt.decode(token, SECRET, algorithms=["HS256"])
assert claims["sub"] == str(USER_ID), "subject claim"
assert claims["exp"] == int((FIXED_NOW + timedelta(hours=1)).timestamp()), "expiry claim"
```

### BAD: Real wall-clock time in an expiry test
```python
token = service.issue(USER_ID)          # exp depends on datetime.now()
# GOOD: inject FakeClock so expiry is deterministic
service = JwtService(config, FakeClock(FIXED_NOW))
```

### BAD: Only the happy path covered
```python
assert service.verify(valid_token).user_id == USER_ID
# GOOD: the rejection paths are the point of a security test
with pytest.raises(TokenExpiredException):
    service.verify(expired_token)
with pytest.raises(InvalidTokenException):
    service.verify(tampered_token)
```
