//#include ltpgnviewer.js

function getNewFENandMoveText(old_move_text,move, mid)
{
  var FEN;
  var move_text;

  //Get new move_text
  var move_list = old_move_text.split(" ");
  filtered_move_list= move_list.filter(function(token){return token.slice(-1) != '.';});
  if (filtered_move_list.length % 2 === 0){ // even # of ply -> white to move
      if (move_list.length < 3){
        move_list.push(move);
      }
      else{
        var next_turn = (parseInt(move_list[move_list.length -3].slice(0,-1))+1)+".";
        move_list.push(next_turn, move);
      }  
    }
    else{ //odd # of ply -> black to move
      move_list.push(move);
    } 
    move_text = move_list.join(" ");
    ply = (filtered_move_list.length+1)+""; // +1 for ply from new  move (+"" converts to string)

    //Apply it to pgn viewer and generate new FEN
    SetPgnMoveText(move_text);
    Init('');
    MoveForward(ply); 
    FEN = GetFEN();

    //submit form with these values
    if( document.forms['hidden_form']){
      var form = document.forms['hidden_form'];
      form.move_text.value = move_text;
      form.position.value = FEN;
      form.ply.value = ply;
      form.mid.value = mid+""; //+"" converts to string
      form.submit()
    }

    //Return new move_text and corresponding FEN    
    return {move_text:move_text, FEN:FEN, ply:ply};
}
