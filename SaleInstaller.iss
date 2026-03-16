; Inno Setup script for Sales Management app

[Setup]
AppName=Sale
AppVersion=1.0
DefaultDirName={pf}\SalesManagement
DefaultGroupName=Sales Management
OutputDir=dist
OutputBaseFilename=SalesManagementSetup
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\Sale\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Sales Management"; Filename: "{app}\Sale.exe"
Name: "{commondesktop}\Sales Management"; Filename: "{app}\Sale.exe"