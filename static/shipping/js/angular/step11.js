function step11($scope, $http){
    $scope.data = [];
    $scope.items = [];
    $scope.curItem = {};
    $scope.editing = false;
    $scope.itemType = 'T';
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

    //invoice uploader
    $scope.invoice_uploader = new plupload.Uploader({
        runtimes : 'html5,flash,html4',
        url : '/shipping/package-information/upload_file/',
        max_file_size : '10mb',
        browse_button : 'pick_invoice_file',
        container: 'uploadInvoiceContainer',
        filters: [
            {
                title: 'Invoice file',
                extensions: 'jpeg,jpg,png,pdf'
            }
        ],
        unique_names: true
        //drop_element: 'dropLicenseArea'
    });

    $scope.invoice_uploader.init();

    $scope.invoice_uploader.bind('Error', function(up, err){
        $scope.invoice_uploader_error = err.message;
        $scope.$apply();
    });

    $scope.invoice_uploader.bind('FilesAdded', function(up, files) {
        $scope.invoice_file_uploaded = false;
        if ($scope.invoice_uploader.files.length > 1){
            $scope.invoice_uploader.removeFile($scope.invoice_uploader.files[0]);
        }
        $scope.invoice_uploader_error = false;
        $scope.$apply();
        //$scope.invoice_uploader.files.splice(0);
    });

    $scope.invoice_uploader.bind('FileUploaded', function(up, files) {
        $scope.invoice_file_uploaded = true;
        $scope.curItem.filename = files.name;
        $scope.curItem.invoice = '/files/'+files.target_name;
        $scope.invoice_uploader_error = false;
        $scope.$apply();

        //create packageinfo object
        $scope.save_item();

    });

    $scope.start_invoice_upload = function(){
        //$scope.save_item();
        $scope.invoice_uploader.start();
        $(".ajax-progress").show();

    }

    $http({
        method: 'GET',
        headers: 'application/x-www-form-urlencoded',
        url: "/shipping/package-information/get-user-items/"
    }).success(function (data, code) {
        $scope.items = data.items;
        $scope.total_Value = data.total_Value;
        $scope.total_Value_N = data.total_Value_N;
        $scope.currency = data.currency;
    });

    $scope.save_item = function(){
        if ($scope.curItem.total_value == undefined && $scope.itemType == 'I'){
            $scope.msg = "Please provide the necessary details and click the Upload Invoice button!";
            return false;
        }

        $scope.curItem.type = $scope.itemType;
        if ($('#add_item_form').valid()){
            $http({
                method: 'POST',
                headers: 'application/x-www-form-urlencoded',
                url: "/shipping/package-information/save-item-data/",
                data: { 'data' : $scope.curItem }

            }).success(function (data, code) {
                //$scope.data = data.data;
                if (data.data == 'ok'){
                    $scope.curItem.id = data.id;
                    $scope.curItem.type = data.type;
                    $scope.items.push($scope.curItem);
                    $scope.curItem = {};
                    $scope.editing = false;
                    $scope.msg = "Saved";
                    $scope.curItem.courier_tracking_number = data.courier_tracking_number
                    $('.labelfor').removeClass('hidden');
                    $('.track_item_number').removeClass('hidden');
                    console.log(data.courier_tracking_number);
                } else {
                    $scope.msg = "There is an error with your input. Please crosscheck.";
                    //alert('Error, try later');
                }
                return false;
            });
        }else {
            //alert('Fill up all fields please!');
            $scope.msg = "There is an error with your input. Please crosscheck.";
        }
        return false;
    }

    $scope.edit_item = function(id){
        if ($scope.editing == true){
            $scope.msg = "Please save the current editing item first";
            return;
        }

        $scope.msg = "You can now edit the selected item";

        $scope.editing = true;
        var _items = $scope.items;
        $scope.items = [];
        var callback = false;
        angular.forEach(_items, function(item){
            if (item.id != id){
                $scope.items.push(item);
            } else {
                $scope.curItem = item;
                if ($scope.curItem.type == 'T'){
                    var to = setTimeout(function(){
                        jQuery('#add').trigger('click');
                    }, 300);
                } else {
                    var to = setTimeout(function(){
                        $('#upl').trigger('click');
                    }, 300);
                }
            }
        });
        if (typeof(callback) == 'function'){
            callback();
        }
    }

    $scope.del_item = function(id){
        var deleteCustomer = confirm('Are you absolutely sure you want to delete this item?');

        if (deleteCustomer) {
            $http({
                method: 'POST',
                headers: 'application/x-www-form-urlencoded',
                url: "/shipping/package-information/del-item-data/",
                data: { 'data' : id, 'delete':'delete' }
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
            return false;
        }

        return false;
    }


}
