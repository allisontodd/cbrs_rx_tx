sudo add-apt-repository -y ppa:ettusresearch/uhd
sudo add-apt-repository -y ppa:johnsond-u/sdr
sudo apt-get update

for thing in $*
do
    case $thing in
        gnuradio)
            sudo DEBIAN_FRONTEND=noninteractive apt-get install -y gnuradio python3-gi gobject-introspection gir1.2-gtk-3.0 python3-cairo python3-gi-cairo
            ;;

        srslte)
            sudo DEBIAN_FRONTEND=noninteractive apt-get install -y srslte
            ;;
    esac
done

sudo sysctl -w net.core.rmem_max=24862979
sudo sysctl -w net.core.wmem_max=24862979

sudo rm /usr/bin/uhd_rx_cfile
chmod +x /local/repository/uhd_rx_cfile
sudo mv /local/repository/uhd_rx_cfile /usr/bin/

chmod +x /local/repository/uhd_siggen_timing
sudo mv /local/repository/uhd_siggen_timing /usr/bin/

chmod +x /local/repository/uhd_siggen_45sec
sudo mv /local/repository/uhd_siggen_45sec /usr/bin/

chmod +x /local/repository/uhd_siggen_90sec
sudo mv /local/repository/uhd_siggen_90sec /usr/bin/

chmod +x /local/repository/iq_to_power.py
sudo mv /local/repository/iq_to_power.py /usr/bin/


sudo ed /etc/sysctl.conf << "EDEND"
a
net.core.rmem_max=24862979
net.core.wmem_max=24862979
.
w
EDEND

#sudo "/usr/lib/uhd/utils/uhd_images_downloader.py -t x310"
