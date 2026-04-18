; AxoLexis Production Installer Script
; Lightweight - downloads Python/dependencies at runtime

#define MyAppName "AxoLexis"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "AxoLexis Labs"
#define MyAppURL "https://axolexis.ai"
#define MyAppExeName "AxoLexis.exe"

[Setup]
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir=installer
OutputBaseFilename=AxoLexis_Setup_v{#MyAppVersion}
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog
DisableProgramGroupPage=yes
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayIcon={app}\{#MyAppExeName}
SetupIconFile=app_icon.ico
ShowLanguageDialog=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "create_shortcuts"; Description: "Create shortcuts"; GroupDescription: "Shortcuts"; Flags: checkedonce

[Files]
; Main executable (launcher)
Source: "dist\AxoLexis.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "app_icon.ico"; DestDir: "{app}"; Flags: ignoreversion

; Requirements file
Source: "requirements.txt"; DestDir: "{app}"; Flags: ignoreversion

; Post-install script
Source: "post_install.ps1"; DestDir: "{app}"; Flags: ignoreversion

; UI files
Source: "ui\*"; DestDir: "{app}\ui"; Flags: ignoreversion recursesubdirs createallsubdirs

; Models files
Source: "models\*"; DestDir: "{app}\models"; Flags: ignoreversion recursesubdirs createallsubdirs

; Data files
Source: "data\*"; DestDir: "{app}\data"; Flags: ignoreversion recursesubdirs createallsubdirs

; Reports folder
Source: "axolexis_intelligent_reports\*"; DestDir: "{app}\axolexis_intelligent_reports"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\app_icon.ico"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; IconFilename: "{app}\app_icon.ico"

[Run]
; Run post-install script with proper execution policy and status
Filename: "powershell.exe"; Parameters: "-ExecutionPolicy Bypass -NoProfile -File ""{app}\post_install.ps1"" -InstallPath ""{app}"""; StatusMsg: "Configuring AxoLexis environment (Please follow the progress in the command window)..."; Flags: waituntilterminated

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

[Code]
var
  SetupAborted: Boolean;

function InitializeSetup(): Boolean;
begin
  Result := True;
  SetupAborted := False;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  ErrorCode: Integer;
  ResultCode: Integer;
begin
  if CurStep = ssPostInstall then
  begin
    Log('Starting post-install configuration...');
  end;
end;

procedure CurPageChanged(CurPageID: Integer);
begin
  if CurPageID = wpFinished then
  begin
    if SetupAborted then
    begin
      MsgBox('Installation was aborted. Check the log file for details.', mbError, MB_OK);
    end;
  end;
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
end;

procedure InitializeWizard();
begin
  WizardForm.WelcomeLabel2.Caption :=
    'This will install AxoLexis on your computer.' + #13#10 + #13#10 +
    'AxoLexis is an intelligent training system that requires Python 3.10+' + #13#10 +
    'and will be downloaded if not found on your system.' + #13#10 + #13#10 +
    'Setup will:' + #13#10 +
    '1. Check for Python (or download if needed)' + #13#10 +
    '2. Create a virtual environment' + #13#10 +
    '3. Install all required dependencies' + #13#10 +
    '4. Create shortcuts' + #13#10 + #13#10 +
    'Click Next to continue.';
end;