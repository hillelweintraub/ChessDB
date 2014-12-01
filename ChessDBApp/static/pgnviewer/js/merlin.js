document.writeln('<OBJECT ID="AgentControl" width=0 height=0 CLASSID="CLSID:D45FD31B-5C6E-11D1-9EC1-00C04FD7081F" \n');
document.writeln(' CODEBASE="#VERSION=2,0,0,0"><br> \n');
document.writeln('</OBJECT><br> \n');
document.writeln('<OBJECT ID="TruVoice" width=0 height=0 CLASSID="CLSID:B8F2846E-CE36-11D0-AC83-00C04FD97575" \n');
document.writeln(' CODEBASE="http://activex.microsoft.com/activex/controls/agent2/tv_enua.exe#VERSION=6,0,0,0"> \n');
document.writeln('</OBJECT>');
document.writeln('<OBJECT ID="SAPI4" WIDTH=0 HEIGHT=0 CLASSID="CLSID:0C7F3F20-8BAB-11d2-9432-00C04F8EF48F" \n');
document.writeln(' CODEBASE="http://activex.microsoft.com/activex/controls/sapi/spchapi.exe#VERSION=4,0,0,0"> \n');
document.writeln('</OBJECT>');
var Merlin;
var MerlinLoaded = false;
var LoadReq;
function LoadMerlin()
{ AgentControl.Connected = true;
  MerlinLoaded = LoadChar("Merlin", "merlin.acs");
  if (!MerlinLoaded) MerlinLoaded = LoadChar("Merlin", "");
  if (!MerlinLoaded) MerlinLoaded = LoadChar("Merlin", "http://agent.microsoft.com/agent2/chars/merlin/merlin.acf");
  if (!MerlinLoaded) return;
  window.status = "";
  InitMerlin();
}
function LoadChar(CharID, CharACS)
{ AgentControl.RaiseRequestErrors = false;
  if (CharACS == "") LoadReq = AgentControl.Characters.Load(CharID);
  else LoadReq = AgentControl.Characters.Load(CharID, CharACS);
  AgentControl.RaiseRequestErrors = true;
  if (LoadReq.Status != 1) return(true);
  return(false);
}
function InitMerlin()
{ Merlin = AgentControl.Characters.Character("Merlin");
  Merlin.LanguageID = 0x409;
  Merlin.Balloon.Style = 0x21C000E;
  Merlin.MoveTo(0, 120);
  Merlin.Show();
}
window.onbeforeunload=UnloadMerlin;
function UnloadMerlin()
{ if (MerlinLoaded) 
  { try { AgentControl.Characters.Unload("Merlin"); } 
    catch(e) { return; }
  }
}
function HideMerlin(){ if (MerlinLoaded) Merlin.Hide(); }
function ShowMerlin(){ if (MerlinLoaded) Merlin.Show(); }
var Pit="",Spd="";
function MerlinPit(vv) { Pit=vv; } 
function MerlinSpd(vv) { Spd=vv; }
function Speak(ss)
{ var tt="";
  if (MerlinLoaded)
  { if (Pit) tt+="\\Pit="+Pit+"\\";
    if (Spd) tt+="\\Spd="+Spd+"\\";
    Merlin.Speak(tt+ChessWords(ss));
  }
}
function ChessWords(ss)
{ var ii, jj, tt=ss;
  while (tt.indexOf('...')>=0) tt=tt.replace('...',', ');
  while (tt.indexOf('..')>=0) tt=tt.replace('..',', ');
  tt=tt.split(" ");
  for(ii=0; ii<tt.length; ii++)
  { jj=0;
    if (tt[ii].lastIndexOf('1')>0) jj=1;
    if (tt[ii].lastIndexOf('2')>0) jj=1;
    if (tt[ii].lastIndexOf('3')>0) jj=1;
    if (tt[ii].lastIndexOf('4')>0) jj=1;
    if (tt[ii].lastIndexOf('5')>0) jj=1;
    if (tt[ii].lastIndexOf('6')>0) jj=1;
    if (tt[ii].lastIndexOf('7')>0) jj=1;
    if (tt[ii].lastIndexOf('8')>0) jj=1;
    if (jj==1)
    { tt[ii]=tt[ii].replace('.',', ');
      tt[ii]=tt[ii].replace('K',' king ');
      tt[ii]=tt[ii].replace('Q',' queen ');
      tt[ii]=tt[ii].replace('R',' rook ');
      tt[ii]=tt[ii].replace('B',' bishop ');
      tt[ii]=tt[ii].replace('N',' knight ');
      tt[ii]=tt[ii].replace('x',' takes on ');
      tt[ii]=tt[ii].replace('=',' promotes to ');
      tt[ii]=tt[ii].replace('+',' check ');
      tt[ii]=tt[ii].replace('#',' checkmate ');
      tt[ii]=tt[ii]+", ";
    }
    else
    { tt[ii]=tt[ii].replace('0-0-0',' queen side castling, ');
      tt[ii]=tt[ii].replace('O-O-O',' queen side castling, ');
      tt[ii]=tt[ii].replace('0-0',' king side castling, ');
      tt[ii]=tt[ii].replace('O-O',' king side castling, ');
    }
  }
  return(tt.join(" "));
}
function MerlinPlay(aa)
{ if (MerlinLoaded)
  { Merlin.Play(aa);
  }
}
LoadMerlin();

