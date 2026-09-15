# Fixed read-only collector. Caller sends bounded data on stdin, never script text.
# No execution-policy bypass, no profiles, no arbitrary expressions or WSL launch.
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
try {
    $raw = [Console]::In.ReadToEnd()
    if ($raw.Length -gt 1048576) { throw 'INPUT_CAP' }
    $request = ConvertFrom-Json -InputObject $raw
    switch ($request.operation) {
        'HOST' {
            $os = Get-CimInstance -ClassName Win32_OperatingSystem
            $cs = Get-CimInstance -ClassName Win32_ComputerSystem
            $processors = @(Get-CimInstance -ClassName Win32_Processor)
            if ($processors.Count -gt 256) { throw 'CPU_CAP' }
            $virtual = [bool]$cs.HypervisorPresent
            foreach ($cpu in $processors) {
                if ($cpu.VirtualizationFirmwareEnabled) { $virtual = $true }
            }
            $packages = @(Get-AppxPackage -Name 'MicrosoftCorporationII.WindowsSubsystemForLinux' |
                Select-Object -Property Name,Version,PackageFullName,Publisher,SignatureKind)
            if ($packages.Count -gt 8) { throw 'PACKAGE_CAP' }
            $result = [ordered]@{
                operation='HOST'; status='OBSERVED';
                boot_utc=$os.LastBootUpTime.ToUniversalTime().ToString('o');
                caption=[string]$os.Caption; build=[string]$os.BuildNumber;
                architecture=[string]$os.OSArchitecture;
                hypervisor_present=[bool]$cs.HypervisorPresent;
                virtualization=$virtual;
                runtime_packages=@($packages | ForEach-Object {
                    @{name=[string]$_.Name;version=[string]$_.Version;
                      identity=[string]$_.PackageFullName;publisher=[string]$_.Publisher;
                      signature_kind=[string]$_.SignatureKind}
                })
            }
        }
        'FEATURES' {
            # WMI read only; do not use DISM here (implicit log/scratch writers).
            $result=[ordered]@{operation='FEATURES';status='OBSERVED';features=@()}
            foreach ($name in @('VirtualMachinePlatform','Microsoft-Windows-Subsystem-Linux')) {
                $f=Get-CimInstance -ClassName Win32_OptionalFeature -Filter ("Name='" + $name + "'")
                if ($null -eq $f) { throw 'FEATURE_UNAVAILABLE' }
                $state = switch ([int]$f.InstallState) { 1 {'Enabled'} 2 {'Disabled'} 3 {'Absent'} default {'Unknown'} }
                $result.features += @{name=$name;state=$state;restart_needed='UNKNOWN'}
            }
        }
        'AUTHENTICODE' {
            # No evaluation or shell expansion. Path remains a data argument.
            $signature=Get-AuthenticodeSignature -LiteralPath ([string]$request.path)
            $thumb=$null
            if ($null -ne $signature.SignerCertificate) {$thumb=$signature.SignerCertificate.Thumbprint}
            $result=@{operation='AUTHENTICODE';status=[string]$signature.Status;thumbprint=$thumb}
        }
        default { throw 'OPERATION_NOT_ALLOWED' }
    }
    $result | ConvertTo-Json -Depth 8 -Compress
    exit 0
} catch {
    # Never print arbitrary exception messages, command lines, paths or stderr.
    [Console]::Out.WriteLine('{"status":"UNAVAILABLE","reason":"HOST_COLLECTOR_FAILED"}')
    exit 11
}
