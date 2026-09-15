# Story 07: Регистрация и вход по коду из письма в приложении — Progress

## Spec
- [x] interview
- [x] story
- [x] mockups
- [x] api-spec
- [x] test-spec

## Tier 1 — Frontend Scenarios (02_UI_Tests.md)

### 1.1 Пользователь открывает приложение, получает код на почту и оказывается внутри
- [x] stage-1 frontend acceptance RED + interface design
- [x] stage-2 frontend implementation lanes
- [x] stage-3 frontend acceptance GREEN + review
- [x] resolve stage-3 cycle proposals (worklog: 20260914T112609Z-stage-3-frontend-1.1.md, P1 Backspace)

## Harvest — Tier 1 → Tier 2

- [~] harvest

## Tier 2 — Frontend Scenarios (02_UI_Tests.md)

### 2.1 Отсчёт начинается с того же значения при часах браузера в другом поясе
- [ ] stage-1 frontend acceptance RED + interface design
- [ ] stage-2 frontend implementation lanes
- [ ] stage-3 frontend acceptance GREEN + review

### 2.2 Пока идёт запрос кода, кнопка недоступна и повторное нажатие второго запроса не создаёт
- [ ] stage-1 frontend acceptance RED + interface design
- [ ] stage-2 frontend implementation lanes
- [ ] stage-3 frontend acceptance GREEN + review

### 2.4 Пауза между отправками ещё не прошла — кнопка закрыта на время, которое назвал сервис
- [ ] stage-1 frontend acceptance RED + interface design
- [ ] stage-2 frontend implementation lanes
- [ ] stage-3 frontend acceptance GREEN + review

### 2.5 Сервис недоступен при запросе кода — одно сообщение и возможность повторить
- [ ] stage-1 frontend acceptance RED + interface design
- [ ] stage-2 frontend implementation lanes
- [ ] stage-3 frontend acceptance GREEN + review

### 3.2 Код с ведущим нулём уходит как строка, ноль на месте
- [ ] stage-1 frontend acceptance RED + interface design
- [ ] stage-2 frontend implementation lanes
- [ ] stage-3 frontend acceptance GREEN + review

### 3.3 Пока идёт проверка кода, кнопка недоступна и второго запроса нет
- [ ] stage-1 frontend acceptance RED + interface design
- [ ] stage-2 frontend implementation lanes
- [ ] stage-3 frontend acceptance GREEN + review

### 3.4 Отклонённый код показывается одним сообщением, поле открыто для новой попытки
- [ ] stage-1 frontend acceptance RED + interface design
- [ ] stage-2 frontend implementation lanes
- [ ] stage-3 frontend acceptance GREEN + review

### 4.1 Отсчёт дошёл до нуля — поле кода закрыто, доступна только повторная отправка
- [ ] stage-1 frontend acceptance RED + interface design
- [ ] stage-2 frontend implementation lanes
- [ ] stage-3 frontend acceptance GREEN + review

### 4.2 «Отправить новый код» приносит новый код, прежний перестаёт действовать, отсчёт начинается заново
- [ ] stage-1 frontend acceptance RED + interface design
- [ ] stage-2 frontend implementation lanes
- [ ] stage-3 frontend acceptance GREEN + review

### 4.3 Повтор внутри паузы — письмо не уходит, кнопка закрывается на время, которое назвал сервис
- [ ] stage-1 frontend acceptance RED + interface design
- [ ] stage-2 frontend implementation lanes
- [ ] stage-3 frontend acceptance GREEN + review

## Tier 2 — Security Scenarios (05_Security_Tests.md)

### 1.1 Токены и идентификаторы не появляются ни на экране, ни в хранилищах браузера
- [ ] stage-1 acceptance RED + contract design
- [ ] approve stage-1 contracts
- [ ] stage-2 implementation lanes
- [ ] stage-3 acceptance GREEN + review

## Tier 2 — Infrastructure Scenarios (04_Infrastructure_Tests.md)

### 1.1 Нет соединения с сервисом — то же сообщение о недоступности, действие можно повторить
- [ ] stage-1 acceptance RED + contract design
- [ ] approve stage-1 contracts
- [ ] stage-2 implementation lanes
- [ ] stage-3 acceptance GREEN + review
