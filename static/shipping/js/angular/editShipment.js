function editShipment($scope, $http){
    $scope.data = [];
    $scope.items = [];
    $scope.curItem = {};
    $scope.editing = false;
    $scope.itemType = 'B';
    $scope.shipment = '';
    $scope.msg = "";

    $scope.safeApply = function(fn) {
      var phase = this.$root.$$phase;
      if(phase == '$apply' || phase == '$digest') {
        if(fn && (typeof(fn) === 'function')) {
          fn();
        }
      } else {
        this.$apply(fn);
      }
    };

    $scope.$watch('itemType', function(){
        $scope.curItem.type = $scope.itemType;
    });

    
    $http({
        method: 'GET',
        headers: 'application/x-www-form-urlencoded',
        url: "/admin/shipment-manager/get-shipment-package-info/"
    }).success(function (data, code) {
        $scope.items = data.items;
    });
    $scope.save_package = function(){
        if ($scope.curItem.item_length == undefined && $scope.itemType == 'B'){
            $scope.msg = "Enter Dimension first!";
            return false;
        }
        $scope.curItem.type = $scope.itemType;
        $scope.curItem.shipment = $scope.shipment;
        if ($('#edit_package_form')){
            $http({
                method: 'POST',
                headers: 'application/x-www-form-urlencoded',
                url: "/admin/shipment-manager/save-shipment-package-info/",
                data: { 'data' : $scope.curItem }
            }).success(function (data, code) {
                //$scope.data = data.data;
                if (data.data == 'ok'){
                    $scope.curItem.id = data.id;
                    $scope.curItem.type = data.type;
                    $scope.curItem.shipment = data.shipment;
                    $scope.items.push($scope.curItem);
                    $scope.curItem = {};
                    $scope.editing = false;
                    $scope.msg = "Saved";
                } else {
                    //alert('Invalid fields, please check to confirm that you have supplied integer values only.');
                }
            });
        } else {
            alert('Fill up all fields please!');
        }
        return false;
    }

    $scope.edit_package = function(id){
        if ($scope.editing == true){
            $scope.msg = "Please save the current editing item first";
            return;
        } 
        $scope.editing = true;
        var _items = $scope.items;
        $scope.items = [];
        var callback = false;
        angular.forEach(_items, function(item){
            if (item.id != id){
                $scope.items.push(item);
            } else {
                $scope.curItem = item;
                if ($scope.curItem.type == 'I'){
                    var to = setTimeout(function(){
                        jQuery('#dim').trigger('click');
                    }, 300);
                } 
            }
        });
        if (typeof(callback) == 'function'){
            callback();
        }
    }

    $scope.del_package = function(id){
        $http({
            method: 'POST',
            headers: 'application/x-www-form-urlencoded',
            url: "/admin/shipment-manager/del-shipment-package-info/",
            data: { 'data' : id }
        }).success(function (data, code) {
            //$scope.data = data.data;
            if (data.data != 'ok'){
                $scope.msg = 'Error, try later';
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
    $http({
        method: 'GET',
        headers: 'application/x-www-form-urlencoded',
        url: "/admin/shipment-manager/get-shipment-item-info/"
    }).success(function (data, code) {
        $scope.items = data.items;
    });
    $scope.save_item = function(){
        if ($scope.curItem.courier_tracking_number == undefined ){
            $scope.msg = "Enter Item Details first!";
            return false;
        }
        $scope.curItem.type = $scope.itemType;
        $scope.curItem.shipment = $scope.shipment;
        if ($('#edit_item_form')){
            $http({
                method: 'POST',
                headers: 'application/x-www-form-urlencoded',
                url: "/admin/shipment-manager/save-shipment-item-info/",
                data: { 'data' : $scope.curItem }
            }).success(function (data, code) {
                //$scope.data = data.data;
                if (data.data == 'ok'){
                    $scope.curItem.id = data.id;
                    $scope.curItem.type = data.type;
                    $scope.curItem.shipment = data.shipment;
                    $scope.items.push($scope.curItem);
                    $scope.curItem = {};
                    $scope.editing = false;
                    $scope.msg = "Saved";
                } else {
                    //alert('Invalid fields, please check to confirm that you have supplied integer values only.');
                }
            });
        } else {
            alert('Fill up all fields please!');
        }
        return false;
    }
    $scope.edit_item = function(id){
        if ($scope.editing == true){
            $scope.msg = "Please save the current editing item first";
            return;
        } 
        $scope.editing = true;
        var _items = $scope.items;
        $scope.items = [];
        var callback = false;
        angular.forEach(_items, function(item){
            if (item.id != id){
                $scope.items.push(item);
            } else {
                $scope.curItem = item;
                if ($scope.curItem.type == 'B'){
                    var to = setTimeout(function(){
                        jQuery('#dim').trigger('click');
                    }, 300);
                } 
            }
        });
        if (typeof(callback) == 'function'){
            callback();
        }
    }

    $scope.del_item = function(id){
        $http({
            method: 'POST',
            headers: 'application/x-www-form-urlencoded',
            url: "/admin/shipment-manager/del-shipment-item-info/",
            data: { 'data' : id }
        }).success(function (data, code) {
            //$scope.data = data.data;
            if (data.data != 'ok'){
                $scope.msg = 'Error, try later';
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
    //$scope.save_do_later = function(){
    //    if ($scope.curItem.do_later == undefined && $scope.itemType == 'I'){
    //        $scope.msg = "Please check the box before clicking save!";
    //        return false;
    //    }
    //    $scope.curItem.type = $scope.itemType;
    //    if ($('#do_later_form').valid()){
    //        $http({
    //            method: 'POST',
    //            headers: 'application/x-www-form-urlencoded',
    //            url: "/account/package-information/save-do-later/",
    //            data: { 'data' : $scope.curItem }
    //        }).success(function (data, code) {
    //            //$scope.data = data.data;
    //            if (data.data == 'ok'){
    //                $scope.curItem.id = data.id;
    //                $scope.curItem.type = data.type;
    //                $scope.items.push($scope.curItem);
    //                $scope.curItem = {};
    //                $scope.editing = false;
    //                $scope.msg = "Saved. You can now proceed to the next page with the Proceed to Shipping Address button below.";
    //            } else {
    //                //alert('Error, try later');
    //            }
    //        });
    //    } else {
    //        //alert('Fill up all fields please!');
    //    }
    //    return false;
    //}

}
