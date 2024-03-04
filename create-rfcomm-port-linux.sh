timeout=30 # seconds
echo "Running hcitool scan for ADCS, timeout "$timeout"s"
adcs_mac_addr=$(timeout "$timeout"s hcitool scan | grep ADCS | awk '{print $1}' 2>/dev/null)

if [ -z "$adcs_mac_addr" ]; then
    echo "Device not found or command terminated"
    exit 1
fi

rfcomm0=$(rfcomm shwo 0)

if [ -n "$rfcomm_channel_0" ]; then
    echo "This rfcomm channel is taken"
    echo "$rfcomm0"
    exit 1
fi

echo "Binding ADCS's MAC addr: $adcs_mac_addr to rfcomm0"
sudo rfcomm bind 0 "$adcs_mac_addr" 1