function step11($scope, $http){
    $scope.data = [];
    $scope.items = {};
    $scope.curItem = {};

    $http({
        method: 'GET',
        headers: 'application/x-www-form-urlencoded',
        url: "/account/package-information/get-user-items/"
    }).success(function (data, code) {
        $scope.items = data.items;
    });

    $scope.save_item = function(){
        if ($('#add_item_form').valid()){
            $http({
                method: 'POST',
                headers: 'application/x-www-form-urlencoded',
                url: "/account/package-information/save-item-data/",
                data: { 'data' : $scope.curItem }
            }).success(function (data, code) {
                //$scope.data = data.data;
                if (data.data == 'ok'){
                    $scope.curItem.id = data.id;
                    $scope.curItem.type = data.type;
                    $scope.items.push($scope.curItem);
                    $scope.curItem = {};
                } else {
                    alert('Error, try later');
                }
                console.log($scope.curItem);
            });
        } else {
            alert('Fill up all fields please!');
        }
        return false;
    }

    $scope.edit_item = function(id){
        var _items = $scope.items;
        $scope.items = [];
        angular.forEach(_items, function(item){
            if (item.id != id){
                $scope.items.push(item);
            } else {
                $scope.curItem = item;
            }
        });
    }

    $scope.del_item = function(id){
        $http({
            method: 'POST',
            headers: 'application/x-www-form-urlencoded',
            url: "/account/package-information/del-item-data/",
            data: { 'data' : id }
        }).success(function (data, code) {
            //$scope.data = data.data;
            if (data.data != 'ok'){
                alert('Error, try later');
            } 
        });
        var _items = $scope.items;
        $scope.items = [];
        angular.forEach(_items, function(item){
            if (item.id != id){
                $scope.items.push(item);
            } 
        });
    }
}
