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

Scenario Outline 3. Add new nurse to staff
    Given User start application
    And User select Zaloga tab
    When Right click anywhere
    Then Context menu should be displayed with two sub options
    When User select 'Dodaj Pielegniarke' options
    Then New row in grid should be added
    When User put data in first column
    And Click Enter
    Then New nurse object should be created
    And data should be displayed
    When User put data in timejob column
    And Click Enter
    Then Timejob should be updated for proper nurse
    And data should be displayed
    
Scenario Outline 4: Update holidays for nurse
    Given User start application
    And User select Zaloga tab
    And there is at least one nurse exists
    When user put "<holiday>" into holiday column
    And click enter
    Then holidays should be set to proper nurse
    And calculation of hours should be run
    And data should be displayed
Examples:
    | Holiday       |
    | 1.01          |
    | 1.02NZ        |
    | 01.03UZ       |
    | 01.01-09.01   |
	| 22.01-07.02UZ |
    
Scenario Outline 5: Update availabilities for nurse
    Given User start application
    And User select Zaloga tab
    And there is at least one nurse exists
    When user put "<availabilities>" into availabilities column
    And click enter
    Then holidays should be set to proper nurse
    And calculation of hours should be run
    And data should be displayed
Examples:
    | availabilities    |
    | 1_D               |

 
Scenario Outline: x. Calculate schedule for month
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
    
    