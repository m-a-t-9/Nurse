TESTS:

Feature:
Scenario Outline: 1. Start Application with files
    Given User start application
    When Application has been started
    And If file nurse.nur already exists
    Then Zaloga tab should be displayed with all staff's data should be loaded
 
 Scenario Outline: 2. Start Application Clear data
    Given User start application
    And If file nurse.nur does not exist
    When Application has been started
    Then Zaloga tab should be displayed
    And Tab should contain grid with columns only
 
Scenario Outline: 3. Calculate schedule for month
    Given User select 'Nowy Grafik from 'Plik' Menu
    And select "<Month>"
    When Schedule
    Then Schedule tab should be displayed and all duties should be planned
    And No error should be displayed
Examples:
    | Month       |
    | Styczen     |
    | Luty        |
    | Marzec      |
    | Kwiecien    |
    | Maj         |
    | Czerwiec    |
    | Lipiec      |
    | Sierpien    |
    | Wrzesien    |
    | Październik |
    | Listopad    |
    | Grudzien    | 
    
    