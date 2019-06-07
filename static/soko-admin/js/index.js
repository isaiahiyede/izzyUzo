angular.module('MyApp')
    .controller('AppCtrl', function ($scope) {

        $scope.myDate = new Date();

        $scope.minDate = new Date(
            $scope.myDate.getFullYear(),
            $scope.myDate.getMonth() - 2,
            $scope.myDate.getDate());

        $scope.maxDate = new Date(
            $scope.myDate.getFullYear(),
            $scope.myDate.getMonth() + 2,
            $scope.myDate.getDate());
    })


.config(function ($mdDateLocaleProvider) {
    // Example of a Spanish localization.
    $mdDateLocaleProvider.months = ['January', 'February', 'March', 'April', 'May', 'June',
                                  'July', 'August', 'September', 'October', 'November', 'December'];
    $mdDateLocaleProvider.shortMonths = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'June',
                                  'July', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    $mdDateLocaleProvider.days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    $mdDateLocaleProvider.shortDays = ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'];
    // Can change week display to start on Monday.
    $mdDateLocaleProvider.firstDayOfWeek = 1;
    // Optional.
    //$mdDateLocaleProvider.dates = [1, 2, 3, 4, 5, 6, 7,8,9,10,11,12,13,14,15,16,17,18,19,
    //                               20,21,22,23,24,25,26,27,28,29,30,31];
    // In addition to date display, date components also need localized messages
    // for aria-labels for screen-reader users.
    $mdDateLocaleProvider.weekNumberFormatter = function (weekNumber) {
        return 'Semana ' + weekNumber;
    };
    $mdDateLocaleProvider.msgCalendar = 'Calendario';
    $mdDateLocaleProvider.msgOpenCalendar = 'Abrir calendario';
});