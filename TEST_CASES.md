# TEST_CASES — Test Case Specification

Версия 0.9.3, до заморозки. **40 тест-кейсов: 32 module (80%) + 8 scenario (20%)**. ID является стабильной ссылкой между ТЗ, таблицей и `unittest`.

| ID | Тип | Источник | Предусловие | Вход | Ожидание | Приоритет |
|---|---|---|---|---|---|---|
| TC-01 | module | 3.2 | — | name="  " | ValueError | high |
| TC-02 | module | 3.2 | — | mass_kg=0 | ValueError | high |
| TC-03 | module | 3.2 | — | tail_span_m=-1 | ValueError | high |
| TC-04 | module | 3.2 | — | max_speed_kmh=0 | ValueError | high |
| TC-05 | module | 3.2 | — | max_depth_m=0 | ValueError | high |
| TC-06 | module | 3.2 | — | energy=101 | ValueError | high |
| TC-07 | module | 3.2 | — | hull_integrity=-1 | ValueError | high |
| TC-08 | module | 3.2 | — | mass_kg=True | TypeError | high |
| TC-09 | module | 3.1–3.2 | — | nan, inf, -inf, 10**400; name с пробелами | ValueError; имя обрезается | high |
| TC-10 | module | 3.3 | new instance | присвоить все 10 публичных атрибутов | AttributeError; состояние прежнее | high |
| TC-11 | module | 3.4.1 | surface | calculate_energy(5, cruise), неверный тип/режим/переполнение | 10 или TypeError/ValueError; атомарность | high |
| TC-12 | module | 3.4.1 | surface | calculate_energy(5, boost) | 20; state unchanged | high |
| TC-13 | module | 3.4.1 | depth=100 | calculate_energy(5, cruise) | 10 (no surcharge) | high |
| TC-14 | module | 3.4.1 | depth=101 | calculate_energy(5, cruise) | 15 | high |
| TC-15 | module | 3.4.2 | energy=100 | move(10, cruise), неверные аргументы, скорость inf | время=0.25, энергия=80; TypeError/ValueError без изменений | high |
| TC-16 | module | 3.4.2 | energy=100 | move(5, boost) | time=1/12; energy=80 | high |
| TC-17 | module | 3.4.2 | energy=100 | move(50, cruise) | energy=0; position=50 | high |
| TC-18 | module | 3.4.3 | depth=0; energy=100 | dive(20); точный расход; неверные типы, nan/inf | cost=2; энергия=98; TypeError/ValueError | high |
| TC-19 | module | 3.4.3 | depth=0 | dive(201), включая hull=0; dive(200) | PodkotiniTooDeep; точная граница допустима | high |
| TC-20 | module | 3.4.3 | energy=1 | dive(20) при energy=1/hull=0; изменение глубины и dive(0) | NoEnergy/Immobilized; подъем через dive допустим | high |
| TC-21 | module | 3.4.4 | depth=20; energy=98 | surface() с 20м и при точном расходе/нехватке | cost=1; нет энергии — NoEnergy | high |
| TC-22 | module | 3.4.4 | depth=0; hull=0 | surface() при depth=0 и hull=0 / на глубине при hull=0 | no-op / Immobilized; атомарность | high |
| TC-23 | module | 3.4.5 | depth=20 | can_overcome(reef), 19.9/20; неверные препятствия | граница False/True; TypeError/ValueError | medium |
| TC-24 | module | 3.4.5 | energy=29 | can_overcome(current) при energy=29/30 | False/True | medium |
| TC-25 | module | 3.4.5 | tail_span=1.8 | can_overcome(narrow_passage) с хвостом 1.8/2/2.01 | True/True/False | medium |
| TC-26 | module | 3.4.5 | depth=0 | can_overcome(surface_net) при depth=0/9.9/10, hull=0 | False/False/True; hull=0 всегда False | medium |
| TC-27 | module | 3.4.6 | energy=80 | recharge(1000), 0/-1/inf/nan/строка/большое int | energy=100 или ValueError/TypeError | high |
| TC-28 | module | 3.4.7 | hull=100 | damage(120), неверные числовые аргументы | hull=0 либо ValueError/TypeError | high |
| TC-29 | module | 3.4.8 | hull=10 | repair(500), неверные числовые аргументы | hull=100 либо ValueError/TypeError | high |
| TC-30 | module | 3.4.2 | hull=0 | move(1) | PodkotiniImmobilized; atomic | high |
| TC-31 | module | 3.4.9 | new instance | get_status() при name с пробелами, energy=45, hull=35 | 7 ключей, корректные значения, trim | high |
| TC-32 | module | 3.4.9 | new instance | редактировать status, сравнить экземпляры словаря и иерархию ошибок | объект прежний, новый dict, наследование | high |
| TC-33 | scenario | 4.2 S1 | new vehicle | pilot: dive20, move10 cruise, move5 boost, surface | position=15; energy=57; depth=0 | high |
| TC-34 | scenario | 4.2 S1 | new vehicle | pilot: cruise10 then boost5 | times 0.25 and 1/12 | medium |
| TC-35 | scenario | 4.2 S2 | new vehicle | pilot: dive120, cruise10, dive201 (ошибка), surface | energy=52; position=10; depth=0 | high |
| TC-36 | scenario | 4.2 S2 | depth=120 | pilot: dive201 | PodkotiniTooDeep; no mutation | high |
| TC-37 | scenario | 4.2 S3 | new vehicle | pilot: cruise4, damage100, move1 | PodkotiniImmobilized; position=4 | high |
| TC-38 | scenario | 4.2 S3 | hull=0 after move4 | pilot: move1 (ошибка), repair25, move1 | energy=90; position=5; hull=25 | high |
| TC-39 | scenario | 4.2 S4 | energy=25 | pilot: dive100, boost10 | PodkotiniNoEnergy; position=0 | high |
| TC-40 | scenario | 4.2 S4 | energy=15 at depth100 | pilot: boost10 (ошибка), surface, recharge30, cruise5 | energy=30; position=5; depth=0 | high |

Каждый тест `test_tc_NN_*` имеет тот же ID в docstring. Тесты с `scenario` используют `Pilot` и паттерн Given–When–Then; остальные — Arrange–Act–Assert.
