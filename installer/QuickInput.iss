#define MyAppName "QuickInput"
#define MyAppVersion "1.1.0"
#define MyAppPublisher "QuickInput"
#define MyAppExeName "QuickInput.exe"
#define MyAppId "{{7F5DE671-BC23-4D78-9098-929A6DE7660D}"

[Setup]
AppId={#MyAppId}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL=https://github.com/NickJay159/QuickInput
AppSupportURL=https://github.com/NickJay159/QuickInput/issues
AppUpdatesURL=https://github.com/NickJay159/QuickInput/releases
DefaultDirName={localappdata}\Programs\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
AllowNoIcons=yes
OutputDir=..\dist
OutputBaseFilename=QuickInput-{#MyAppVersion}-setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
SetupIconFile=..\icon.ico
LicenseFile=..\LICENSE
UninstallDisplayIcon={app}\{#MyAppExeName}
VersionInfoVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription={#MyAppName} Installer
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#MyAppVersion}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "chinesesimplified"; MessagesFile: ".\ChineseSimplified.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "startupicon"; Description: "{cm:AutoStartQuickInput}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[CustomMessages]
english.AutoStartQuickInput=Start QuickInput when I sign in
chinesesimplified.AutoStartQuickInput=登录 Windows 时启动 QuickInput

[Files]
Source: "..\dist\QuickInput.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\dist\icon.png"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\icon.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; IconFilename: "{app}\icon.ico"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; IconFilename: "{app}\icon.ico"; Tasks: desktopicon
Name: "{userstartup}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; IconFilename: "{app}\icon.ico"; Tasks: startupicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
function SelectedAppLanguage(): String;
begin
  if ActiveLanguage = 'english' then
    Result := 'en_US'
  else
    Result := 'zh_CN';
end;

procedure WriteDefaultSettings(SettingsFile: String);
begin
  SetIniString('hotkey', 'label', 'Ctrl+[', SettingsFile);
  SetIniString('hotkey', 'modifiers', '16386', SettingsFile);
  SetIniString('hotkey', 'virtual_key', '219', SettingsFile);
  SetIniString('popup', 'width', '520', SettingsFile);
  SetIniString('popup', 'height', '560', SettingsFile);
  SetIniString('paste', 'delay_ms', '120', SettingsFile);
  SetIniString('paste', 'clipboard_restore_delay_ms', '1000', SettingsFile);
  SetIniString('ui', 'language', SelectedAppLanguage(), SettingsFile);
  SetIniString('ui', 'theme', 'system', SettingsFile);
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  SettingsFile: String;
begin
  if CurStep <> ssPostInstall then
    Exit;

  SettingsFile := ExpandConstant('{userappdata}\QuickInput\settings.ini');
  ForceDirectories(ExtractFileDir(SettingsFile));

  if not FileExists(SettingsFile) then
  begin
    WriteDefaultSettings(SettingsFile);
    Exit;
  end;

  if GetIniString('ui', 'language', '', SettingsFile) = '' then
    SetIniString('ui', 'language', SelectedAppLanguage(), SettingsFile);
  if GetIniString('ui', 'theme', '', SettingsFile) = '' then
    SetIniString('ui', 'theme', 'system', SettingsFile);
end;
