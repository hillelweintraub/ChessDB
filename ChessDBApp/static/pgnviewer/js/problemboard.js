function WriteBoard(sshowcapt)
{ ImageOffset=document.images.length;
  var ImageStyle="";
  if (Border)
  { if (document.layers) ImageStyle="border="+Border+" ";
    else ImageStyle="style='border-width:"+Border+"px; border-style:solid; border-color:"+BorderColor+"' ";
  }
  document.writeln("<table border=0 cellpadding=1 cellspacing=0><tr><td bgcolor='#404040'>");
  document.write("<TABLE border="+(Border+2)+" cellpadding=0 cellspacing=0><TR><TD>");
  if (!document.layers) document.writeln("<div id='Board'>");
  document.write("<TABLE border=0 cellpadding=0 cellspacing=0><TR>");

  for (var ii=0; ii<64; ii++)
  { if ((9*ii-ii%8)%16==0) document.write("<TD background='"+ImagePath+"w.gif'>");
    else document.write("<TD background='"+ImagePath+"b.gif'>");
    document.write("<IMG SRC='"+ImagePath+"t.gif' "+ImageStyle+" id='"+ii+"' onMouseDown='BoardClick("+ii+")'></TD>");
    if (ii%8==7)
    { if (ii<63) document.write("</TR><TR>");
      else
      { document.writeln("</TR></TABLE>");
        if (!document.layers) document.writeln("</div><div id='Canvas' style='position:relative;z-index:100'></div>");
        document.writeln("</TD></TR></TABLE>");
      }
    }    
  }
  document.writeln("</td><th><img name='RightLabels' src='"+ImagePath+"8_1.gif' onMouseDown='RotateBoard(! isRotated)' title='rotate board' alt='rotate board'></th>");
  document.writeln("<td style='vertical-align:middle'>");
  if (sshowcapt)
  { document.writeln("<table cellpadding=0 cellspacing=0 style='border:1px solid #000000' onMouseDown='ShowCapturedPieces(! isCapturedPieces)' title='show/hide captured pieces'>");
    for (ii=0; ii<8; ii++) 
    { document.writeln("<tr>");
      for (jj=0; jj<4; jj++)  document.writeln("<td style='padding-top:"+Border+"px;padding-bottom:"+Border+"px'><img src='"+ImagePath+"1x1.gif'></td>");
      document.writeln("</tr>");
    }
    document.writeln("</table>");
  }
  document.writeln("</td></tr>");
  document.writeln("<tr><th><img name='BottomLabels' src='"+ImagePath+"a_h.gif' onMouseDown='SetDragDrop(! isDragDrop)' title='piece animation on/off' alt='piece animation on/off'></th>");
  document.writeln("<td colspan=2><img src='"+ImagePath+"1x1.gif' width=7 height=7 border=1 onMouseDown='SwitchLabels()' title='show/hide labels' alt='show/hide labels'></td></tr></table>");
}

function WriteButtons()
{ var ii, nn=0, ss=0;
  if (document.getElementById) //adjust button size
  { if (ImagePath)
    { for (ii=0; ii<ImagePath.length; ii++)
      { if (isNaN(ImagePath.charAt(ii))) nn=0;
        else { nn*=10; nn+=parseInt(ImagePath.charAt(ii)); ss=nn; }
      }
    }
    if (ss==0) ss=31;
    ss+=2*Border;
    if (ss>27) ss-=8;
    else ss=19;
  }
  else ss=25;
  document.writeln("<div id='buttons' style='display:none'>");
  document.writeln("<TABLE border=0 cellpadding=1 cellspacing=0><TR>");
  document.writeln("<TD><input type=button value='I&lt;' width="+eval(ss-4)+" style='width:"+ss+"px' id='btnInit' onClick='Init(\"\")'></TD>");
  document.writeln("<TD><input type=button value='&lt;&lt;' width="+eval(ss-4)+" style='width:"+ss+"px' id='btnMB10' onClick='MoveBack(10)'></TD>");
  document.writeln("<TD><input type=button value='&lt;' width="+eval(ss-4)+" style='width:"+ss+"px' id='btnMB1' onClick='MoveBack(1)'></TD>");
  document.writeln("<TD><input type=button value='&gt;' width="+eval(ss-4)+" style='width:"+ss+"px' id='btnMF1' onClick='MoveForward(1)'></TD>");
  document.writeln("<TD><input type=button value='&gt;&gt;' width="+eval(ss-4)+" style='width:"+ss+"px' id='btnMF10' onClick='MoveForward(10)'></TD>");
  document.writeln("<TD><input type=button value='&gt;I' width="+eval(ss-4)+" style='width:"+ss+"px' id='btnMF1000' onClick='MoveForward(1000)'></TD>");
  document.writeln("<TD><input type=button value='play' width="+eval(2*ss-4)+"px style='width:"+(2*ss)+"px' id='btnPlay' name='AutoPlay' onClick='SwitchAutoPlay()'></TD>");
  document.writeln("<TD><select name='Delay' onChange='SetDelay(this.options[selectedIndex].value)' SIZE=1>");
  document.writeln("<option value=1000>fast");
  document.writeln("<option value=2000>med.");
  document.writeln("<option value=3000>slow");
  document.writeln("</select>");
  document.writeln("</TD></TR></TABLE>");
  document.writeln("<BR></div>");
}
function WritePosition()
{ var ii, nn=0, ss=0;
  if (document.getElementById) //adjust button size
  { if (ImagePath)
    { for (ii=0; ii<ImagePath.length; ii++)
      { if (isNaN(ImagePath.charAt(ii))) nn=0;
        else { nn*=10; nn+=parseInt(ImagePath.charAt(ii)); ss=nn; }
      }
    }
    if (ss==0) ss=31;
    ss+=2*Border;
    if (ss>27) ss-=8;
    else ss=19;
  }
  else ss=25;
  document.writeln("<TABLE border=0 cellpadding=1 cellspacing=0><TR>");
  document.writeln("<TD style='vertical-align:middle'>Position after:</TD>");
  document.writeln("<TH><input type=text name='Position' value='' width="+eval(4*ss-4)+" style='width:"+eval(4*ss)+"px' id='inpPos' size=14></TH>");
  document.writeln("<TD><input type=button value='print' width="+eval(2*ss-4)+" style='width:"+eval(2*ss)+"px' onClick='PrintPosition()'></TD>");
  document.writeln("</TR></TABLE>");
}
function WriteHintButtons()
{ document.writeln("<div id='hintButtons' style='display:none'>");
  document.writeln("<TABLE border=0 cellpadding=1 cellspacing=0><TR>");
  document.writeln("<TD><input type=button name='buttonNextMove' value='show next move' width=120 style='width:121' onClick='ShowNextMoves(2)'></TD>");
  document.writeln("<TD><input type=button name='buttonSolution' value='show solution' width=120 style='width:121' onClick='ShowSolution()'></TD>");
  document.writeln("</TR></TABLE></div>");
}
var isSolved=false;
var wrongMoves=0;
var shownMoves=0;
var wrongMovesNew=0;
//function UserMove is called whenever you make a move by clicking on the board
//you can change the code if you want to do anything else here
function UserMove(isTextMove, MoveText)
{ if (isSolved) return;
  mm=MoveCount;
  if ((isTextMove)&&(MoveText.indexOf("?")<0))
  { var mm=MoveCount;
    ExecCommand(true);
    MoveForward(1);
    ExecCommand(false);
    if (mm==MoveCount)
    { if (shownMoves==0) alert("Congratulations, you solved the problem.\nNumber of wrong moves: "+wrongMoves);
      ShowSolution();
    }
    else
    { wrongMovesNew=0;
      if (document.getElementById)
        document.getElementById('hintButtons').style.display="none";
    }
  }
  else
  { alert("Sorry, this is not the correct move.");
    wrongMoves++;
    MoveBack(1);
    ExecCommand(true);
    SetMove(MoveCount+1,CurVar);
    ExecCommand(false);
    MoveBack(1);
    wrongMovesNew++;
    if ((wrongMovesNew==3)&&(document.getElementById))
      document.getElementById('hintButtons').style.display="inline";
  }
}
function ShowNextMoves(nn)
{ var mm=MoveCount;
  if (nn%2==0)
  { shownMoves++;
    wrongMovesNew=0;
    if (document.getElementById)
      document.getElementById('hintButtons').style.display="none";
  }
  ExecCommand(true);
  MoveForward(1);
  ExecCommand(false);
  if (mm==MoveCount) ShowSolution();
  else
  { if (nn>1) setTimeout("ShowNextMoves("+(nn-1)+")",1000);
  }
}
function ShowSolution()
{ if (document.getElementById)
  { isSolved=true;
    document.getElementById('gameText').innerHTML=GetHTMLMoveText();
    document.getElementById('buttons').style.display="inline";
    document.getElementById('hintButtons').style.display="none";
  }
}
