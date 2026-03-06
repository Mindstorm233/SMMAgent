from draw.renderer import draw_chip

# 1. Prepare the revised data
chip_data = {
  "reasoning": "According to the protocol description, it is necessary to achieve single-cell droplet encapsulation, including injection, mixing, droplet generation, and collection of cell suspension, oil phase, and lysis buffer. Due to the fact that the components provided in the component library (M4, M5, P8) are mainly used for reagent merging and do not fully match the droplet generation protocol, they can be adapted based on existing components. M5 is used as the main mixing module because it is designed for small volume merging through serial microcavities, suitable for mixing cell suspensions and lysates. Use P8 as a storage module to pre install reagents. Additional inlets and outlets need to be added to simulate oil phase injection and droplet collection. Due to the lack of specialized droplet generation components (such as flow focusing structures), the mixing function of M5 is used to approximate the mixing step, assuming that droplet generation occurs at the outlet. The operation plan includes sequentially injecting reagents, starting the carrier solution for mixing, and then collecting.",
  "instances": [
    {
      "inst_id": "U001",
      "lib_id": "P8",
      "role": "storage_cell_suspension",
      "domain": "meter",
      "phase": "sample_prep",
      "ports_liquid": "liq_in_1,liq_out_1",
      "ports_air": "air_1",
      "ports_act": "",
      "ports_thermal": "",
      "ports_magnetic": "",
      "reagent_name": "cell_suspension",
      "reagent_volume_uL": "50",
      "reagent_state": "liquid",
      "param_override": ""
    },
    {
      "inst_id": "U002",
      "lib_id": "P8",
      "role": "storage_oil",
      "domain": "meter",
      "phase": "sample_prep",
      "ports_liquid": "liq_in_1,liq_out_1",
      "ports_air": "air_1",
      "ports_act": "",
      "ports_thermal": "",
      "ports_magnetic": "",
      "reagent_name": "oil",
      "reagent_volume_uL": "100",
      "reagent_state": "liquid",
      "param_override": ""
    },
    {
      "inst_id": "U003",
      "lib_id": "P8",
      "role": "storage_lysis_buffer",
      "domain": "meter",
      "phase": "lysis",
      "ports_liquid": "liq_in_1,liq_out_1",
      "ports_air": "air_1",
      "ports_act": "",
      "ports_thermal": "",
      "ports_magnetic": "",
      "reagent_name": "lysis_buffer",
      "reagent_volume_uL": "50",
      "reagent_state": "liquid",
      "param_override": ""
    },
    {
      "inst_id": "U004",
      "lib_id": "M5",
      "role": "mixer_droplet_generator",
      "domain": "mix",
      "phase": "sample_prep",
      "ports_liquid": "liq_in_1,liq_out_1",
      "ports_air": "air_1",
      "ports_act": "",
      "ports_thermal": "",
      "ports_magnetic": "",
      "reagent_name": "",
      "reagent_volume_uL": "0",
      "reagent_state": "empty",
      "param_override": ""
    },
    {
      "inst_id": "U005",
      "lib_id": "P8",
      "role": "collection_chamber",
      "domain": "interface",
      "phase": "detect",
      "ports_liquid": "liq_in_1,liq_out_1",
      "ports_air": "air_1",
      "ports_act": "",
      "ports_thermal": "",
      "ports_magnetic": "",
      "reagent_name": "",
      "reagent_volume_uL": "0",
      "reagent_state": "empty",
      "param_override": ""
    }
  ],
  "connections": [
    {
      "edge_id": "E001",
      "from_inst": "U001",
      "from_port": "liq_out_1",
      "to_inst": "U004",
      "to_port": "liq_in_1",
      "channel": "liquid",
      "domain": "mix",
      "phase": "sample_prep"
    },
    {
      "edge_id": "E002",
      "from_inst": "U002",
      "from_port": "liq_out_1",
      "to_inst": "U004",
      "to_port": "liq_in_1",
      "channel": "liquid",
      "domain": "mix",
      "phase": "sample_prep"
    },
    {
      "edge_id": "E003",
      "from_inst": "U003",
      "from_port": "liq_out_1",
      "to_inst": "U004",
      "to_port": "liq_in_1",
      "channel": "liquid",
      "domain": "mix",
      "phase": "cross_phase"
    },
    {
      "edge_id": "E004",
      "from_inst": "U004",
      "from_port": "liq_out_1",
      "to_inst": "U005",
      "to_port": "liq_in_1",
      "channel": "liquid",
      "domain": "interface",
      "phase": "cross_phase"
    }
  ],
  "plan": [
    {
      "step_id": 1,
      "action": "press",
      "target_inst": "U001",
      "target_port": "act_1",
      "value": "pressure=10",
      "duration_s": 5,
      "depends_on": "",
      "domain": "meter",
      "phase": "sample_prep"
    },
    {
      "step_id": 2,
      "action": "press",
      "target_inst": "U003",
      "target_port": "act_1",
      "value": "pressure=10",
      "duration_s": 5,
      "depends_on": "1",
      "domain": "meter",
      "phase": "lysis"
    },
    {
      "step_id": 3,
      "action": "mix_bubble",
      "target_inst": "U004",
      "target_port": "air_1",
      "value": "frequency=5",
      "duration_s": 10,
      "depends_on": "2",
      "domain": "mix",
      "phase": "sample_prep"
    },
    {
      "step_id": 4,
      "action": "press",
      "target_inst": "U002",
      "target_port": "act_1",
      "value": "pressure=15",
      "duration_s": 10,
      "depends_on": "3",
      "domain": "meter",
      "phase": "sample_prep"
    },
    {
      "step_id": 5,
      "action": "wait",
      "target_inst": "",
      "target_port": "",
      "value": "",
      "duration_s": 30,
      "depends_on": "4",
      "domain": "utility",
      "phase": "utility"
    }
  ]
}

# 2. Execute drawing
# Support .svg, .png, .pdf etc.
draw_chip(chip_data, "microfluidic_layout.pdf")

print("Rendering completed! Please check the microfluidic_layout file in current directory.")
