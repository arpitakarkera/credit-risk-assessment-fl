var conn;
var model_parameters;
var training_status;
var updates_status;
var check_status;
var count = 0;
function fetchConnectionStatus(){
 $.ajax({
  url: '/getConnectionStatus',
  type: 'POST',
  success: function(response){
    console.log(response)
  $("#message").html(response)
  conn = response
  if(conn == "Connection not established"){
    setTimeout(fetchConnectionStatus,1000);
  }
  else{
    setTimeout(fetchModelStatus,2000);
  }
  }
 });
}

function fetchModelStatus(){
 $.ajax({
  url: '/getModelStatus',
  type: 'POST',
  success: function(response){
    console.log(response)
  $("#message").html(response)
  model_parameters = response
  if(model_parameters == "Waiting for model to be received"){
    setTimeout(fetchModelStatus,1000);
  }
  else{
    setTimeout(fetchTrainingStatus,2000);
  }
  }
 });
}
function fetchTrainingStatus(){
 $.ajax({
  url: '/getTrainingStatus',
  type: 'POST',
  success: function(response){
    console.log(response)
  $("#message").html(response)
  training_status = response
  if(training_status == "Training Received Model on Local Data"){
    setTimeout(fetchTrainingStatus,1000);
  }
  else{
    setTimeout(fetchUpdatesStatus,2000);
  }
  }
 });
}

function fetchUpdatesStatus(){
 $.ajax({
  url: '/getUpdateStatus',
  type: 'POST',
  success: function(response){
    console.log(response)
  $("#message").html(response)
  updates_status = response
  if(updates_status == "Federated Averaging in Process"){
    setTimeout(fetchUpdatesStatus,1000);
  }
  else{
    setTimeout(checkRoundStatus,2000);
  }
  }
 });
}

function checkRoundStatus(){
 $.ajax({
  url: '/checkRoundStatus',
  type: 'POST',
  success: function(response){
    console.log(response)
  $("#message").html(response)
  check_status = response
  if(check_status == "Server averaging the updates"){
    setTimeout(checkRoundStatus,1000);
  }
  else{
    count+=1;
    if(count>=2){
      $('#buttonDownload').css('visibility', 'visible');
      $("#message").html('Training completed successfully')
    }
    else{
      setTimeout(fetchModelStatus,2000);
    }
  }
  }
 });
}



$(document).ready(function(){
  fetchConnectionStatus();
});
