#!/usr/bin/python

"""
This profile allows the allocation of resources for over-the-air
operation on the POWDER platform. Specifically, the profile has
options to request the allocation of SDR radios in rooftop 
base-stations.

Map of deployment is here:
https://www.powderwireless.net/map

This profile works with the CBRS band (3400 - 3800 MHz) NI/Ettus X310
base-station radios in POWDER.  The naming scheme for these radios is
cbrssdr1-&lt;location&gt;, where 'location' is one of the rooftop names
shown in the above map. Each X310 is paired with a compute node (by default
a Dell d740).


"""

# Library imports
import geni.portal as portal
import geni.rspec.pg as rspec
import geni.rspec.emulab.pnext as pn
import geni.rspec.emulab.spectrum as spectrum
import geni.rspec.igext as ig


# Global Variables
# x310_node_disk_image = \
#         "urn:publicid:IDN+emulab.net+image+reu2020:cir_localization"
x310_node_disk_image = \
        "urn:publicid:IDN+emulab.net+image+emulab-ops:UBUNTU18-64-GR38-PACK"
setup_command = "/local/repository/startup.sh"
# installs = ["gnuradio"]

# Top-level request object.
request = portal.context.makeRequestRSpec()

# Helper function that allocates a PC + X310 radio pair, with Ethernet
# link between them.
def x310_node_pair(idx, x310_radio_name, node_type): #installs
    radio_link = request.Link("radio-link-%d" % idx)

    node = request.RawPC("%s-comp" % x310_radio_name)
    node.hardware_type = node_type
    node.disk_image = x310_node_disk_image

    # service_command = " ".join([setup_command] + installs)
    # node.addService(rspec.Execute(shell="bash", command=service_command))

    node_radio_if = node.addInterface("usrp_if")
    node_radio_if.addAddress(rspec.IPv4Address("192.168.40.1",
                                               "255.255.255.0"))
    radio_link.addInterface(node_radio_if)

    radio = request.RawPC("%s-x310" % x310_radio_name)
    radio.component_id = x310_radio_name
    radio_link.addNode(radio)

# Node type parameter for PCs to be paired with X310 radios.
# Restricted to those that are known to work well with them.
portal.context.defineParameter(
    "nodetype",
    "Compute node type",
    portal.ParameterType.STRING, "d740",
    ["d740","d430"],
    "Type of compute node to be paired with the X310 Radios",
)

# List of CBRS rooftop X310 radios.
rooftop_names = [
    ("cbrssdr1-bes",
     "Behavioral"),
    ("cbrssdr1-browning",
     "Browning"),
    ("cbrssdr1-dentistry",
     "Dentistry"),
    ("cbrssdr1-fm",
     "Friendship Manor"),
    ("cbrssdr1-honors",
     "Honors"),
    ("cbrssdr1-meb",
     "MEB"),
    ("cbrssdr1-smt",
     "SMT"),
    ("cbrssdr1-ustar",
     "USTAR"),
     ("cbrssdr1-hospital",
     "Hospital"),
]

# Frequency/spectrum parameters
portal.context.defineStructParameter(
    "freq_ranges", "Range", [],
    multiValue=True,
    min=1,
    multiValueTitle="Frequency ranges for over-the-air operation.",
    members=[
        portal.Parameter(
            "freq_min",
            "Frequency Min",
            portal.ParameterType.BANDWIDTH,
            3550.0,
            longDescription="Values are rounded to the nearest kilohertz."
        ),
        portal.Parameter(
            "freq_max",
            "Frequency Max",
            portal.ParameterType.BANDWIDTH,
            3560.0,
            longDescription="Values are rounded to the nearest kilohertz."
        ),
    ])
    
# Multi-value list of x310+PC pairs to add to experiment.
portal.context.defineStructParameter(
    "radios", "X310 CBRS Radios", [],
    multiValue=True,
    min=1,
    multiValueTitle="CBRS Radios.",
    members=[
        portal.Parameter(
            "radio_name",
            "Rooftop base-station X310",
            portal.ParameterType.STRING,
            rooftop_names[0],
            rooftop_names)
    ])

#portal.context.defineStructParameter(
#    "radios", "X310 CBRS Radios",
#    multiValue=False,
#    members=[
#        portal.Parameter(
#            "radio_name1",
#            "Rooftop base-station X310",
#            portal.ParameterType.STRING,
#            rooftop_names[0],
#            rooftop_names)
#    ])

# Bind and verify parameters
params = portal.context.bindParameters()

for i, frange in enumerate(params.freq_ranges):
    if frange.freq_min < 3400 or frange.freq_min > 3800 \
       or frange.freq_max < 3400 or frange.freq_max > 3800:
        perr = portal.ParameterError("Frequencies must be between 3400 and 3800 MHz", ["freq_ranges[%d].freq_min" % i, "freq_ranges[%d].freq_max" % i])
        portal.context.reportError(perr)
    if frange.freq_max - frange.freq_min < 1:
        perr = portal.ParameterError("Minimum and maximum frequencies must be separated by at least 1 MHz", ["freq_ranges[%d].freq_min" % i, "freq_ranges[%d].freq_max" % i])
        portal.context.reportError(perr)

portal.context.verifyParameters()

# Request frequency range(s)
for frange in params.freq_ranges:
    request.requestSpectrum(frange.freq_min, frange.freq_max, 100)

# Request PC + X310 resource pairs.
for i, radios in enumerate(params.radios):
	x310_node_pair(i, radios.radio_name, params.nodetype) #installs

# Emit!
portal.context.printRequestRSpec()
