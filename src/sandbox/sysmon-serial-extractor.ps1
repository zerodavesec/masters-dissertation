$ErrorActionPreference = "Stop"

$debug = "C:\Temp\sysmon-serial-extractor.log"

function Log($msg) {
    "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') $msg" | Out-File -FilePath $debug -Append
}

Log "SCRIPT START"

$port = New-Object System.IO.Ports.SerialPorts

$port.PortName = "COM1"
$port.BaudRate = 115200
$port.Parity = [System.IO.Ports.Parity]::None
$port.DataBits = 8
$port.StopBits = [System.IO.Ports.StopBits]::One
$port.Handshake = [System.IO.Ports.Handshake]::None
$port.DtrEnable = $true
$port.RtsEnable = $true
$port.NewLine = "`r`n"
$port.WriteTimeout = 5000

try {
    Log "OPENING SERIAL"
    $port.Open()
    Log "SERIAL OPEN"

    # Test for confirmation that COM1 workds -> Confirmed to work.
    # $port.WriteLine("NXLOG SERIAL TEST")

    Log "SERIAL TEST SENT"

    while ($true) {
        $line = [Console]::In.ReadLine()

        if ($null -eq $line) {
            Log "STDIN CLOSED"
            break
        }

        Log "RX: $line"
        $port.WriteLine($line)

        Log "TX OK"

    }
}
catch {
    Log "ERROR: $($_.Exception.Message)"
}
finally {
    Log "CLOSING"

    if ($port.IsOpen) {
        $port.Close()
    }
}
