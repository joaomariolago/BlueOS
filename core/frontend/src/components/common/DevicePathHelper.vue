<template>
  <div v-if="board_connector">
    <template v-if="inline">
      <div v-if="usbOverlayInfo" class="usb-overlay">
        {{ usbOverlayInfo }}
      </div>
      <object
        :class="inline_name"
        type="image/svg+xml"
        :data="board_image"
        :style="`height: ${height}`"
      />
    </template>
    <v-tooltip
      v-else
      top
    >
      <template #activator="{ on, attrs }">
        <v-icon
          v-if="board_connector !== null"
          v-bind="attrs"
          v-on="on"
        >
          mdi-eye
        </v-icon>
      </template>
      <div v-if="usbOverlayInfo" class="usb-overlay">
        {{ usbOverlayInfo }}
      </div>
      <object
        :class="svgName"
        type="image/svg+xml"
        :data="board_image"
        :style="`height: ${height}`"
      />
    </v-tooltip>
  </div>
</template>

<script lang="ts">
import { v4 as uuid } from 'uuid'
import Vue from 'vue'

import navigator_image from '@/assets/img/devicePathHelper/navigator.svg'
import raspberry_pi3_image from '@/assets/img/devicePathHelper/rpi3b.svg'
import raspberry_pi4_image from '@/assets/img/devicePathHelper/rpi4b.svg'
import raspberry_pi5_image from '@/assets/img/devicePathHelper/rpi5.svg'
import system_information from '@/store/system-information'
import { Dictionary } from '@/types/common'

enum BoardType {
  Rpi4B = 'Rpi4B',
  Rpi3B = 'Rpi3B',
  Rpi5 = 'Rpi5',
  Navigator = 'Navigator',
  Unknown = 'Unknown'
}

const standard_connector_map: Dictionary<string> = {
  '/dev/ttyS0': 'serial1',
  '/dev/ttyAMA1': 'serial3',
  '/dev/ttyAMA2': 'serial4',
  '/dev/ttyAMA3': 'serial5',
  // Pi4
  '/dev/serial/by-path/platform-fd500000.pcie-pci-0000:01:00.0-usb-0:1.3': 'top-left',
  '/dev/serial/by-path/platform-fd500000.pcie-pci-0000:01:00.0-usb-0:1.4': 'bottom-left',
  '/dev/serial/by-path/platform-fd500000.pcie-pci-0000:01:00.0-usb-0:1.1': 'top-right',
  '/dev/serial/by-path/platform-fd500000.pcie-pci-0000:01:00.0-usb-0:1.2': 'bottom-right',
  // Pi3
  '/dev/serial/by-path/platform-3f980000.usb-usb-0:1.5:1': 'bottom-right',
  '/dev/serial/by-path/platform-3f980000.usb-usb-0:1.4:1': 'top-right',
  '/dev/serial/by-path/platform-3f980000.usb-usb-0:1.3:1': 'bottom-left',
  '/dev/serial/by-path/platform-3f980000.usb-usb-0:1.2:1': 'top-left',
  // Pi5
  '/dev/serial/by-path/platform-xhci-hcd.1-usb-0:1': 'top-left',
  '/dev/serial/by-path/platform-xhci-hcd.0-usb-0:1': 'bottom-left',
  '/dev/serial/by-path/platform-xhci-hcd.0-usb-0:2': 'top-right',
  '/dev/serial/by-path/platform-xhci-hcd.1-usb-0:2': 'bottom-right',

}

export default Vue.extend({
  name: 'DevicePathHelper',
  props: {
    device: {
      type: String,
      required: true,
    },
    inline: {
      type: Boolean,
      required: false,
      default: false,
    },
    height: {
      type: String,
      required: false,
      default: '250px',
    },
  },
  data: () => ({
    imgObject: null as Document | null | undefined,
    svgName: `device-path-helper-img-${uuid()}`,
  }),
  computed: {
    is_kernel_6() : boolean {
      return system_information.system?.info?.kernel_version?.startsWith('6.') ?? false
    },
    updated_connector_map() : Dictionary<string> {
      if (this.is_kernel_6) {
        switch (this.get_host_board_type) {
          case BoardType.Rpi5:
            return {
              ...standard_connector_map,
              '/dev/ttyAMA0': 'serial1',
              '/dev/ttyAMA2': 'serial3',
              '/dev/ttyAMA3': 'serial4',
              '/dev/ttyAMA4': 'serial5',
            }
          case BoardType.Rpi4B:
            return {
              ...standard_connector_map,
              '/dev/ttyS0': 'serial1',
              '/dev/ttyAMA3': 'serial3',
              '/dev/ttyAMA4': 'serial4',
              '/dev/ttyAMA5': 'serial5',
            }
          default:
            return standard_connector_map
        }
      }
      return standard_connector_map
    },
    inline_name(): string {
      return `${this.svgName}-inline`
    },
    serial_port_path(): string {
      /* returns the by-path path for the serial port if available */
      return system_information.serial?.ports?.find((a) => a.name === this.device)?.by_path ?? this.device as string
    },
    get_host_board_type() : BoardType {
      switch (true) {
        case system_information.platform?.raspberry?.model?.includes('Raspberry Pi 4'):
          return BoardType.Rpi4B
        case system_information.platform?.raspberry?.model?.includes('Raspberry Pi 5'):
          return BoardType.Rpi5
        case system_information.platform?.raspberry?.model?.includes('Raspberry Pi 3'):
          return BoardType.Rpi3B
        default:
          return BoardType.Unknown
      }
    },
    board_type() : BoardType {
      /* Detects board type between navigator and Rpi4 */
      switch (true) {
        case this.serial_port_path.includes('ttyAMA'):
        case this.serial_port_path.includes('ttyS0'):
          return BoardType.Navigator
        case this.serial_port_path.includes('platform-3f980000'):
          return BoardType.Rpi3B
        case this.serial_port_path.includes('platform-fd500000'):
          return BoardType.Rpi4B
        case this.get_host_board_type === BoardType.Rpi5 && this.serial_port_path.includes('platform-xhci-hcd'):
          return BoardType.Rpi5
        default:
          return BoardType.Unknown
      }
    },
    board_image() : string {
      switch (this.board_type) {
        case BoardType.Navigator:
          return navigator_image
        case BoardType.Rpi4B:
          return raspberry_pi4_image
        case BoardType.Rpi3B:
          return raspberry_pi3_image
        case BoardType.Rpi5:
          return raspberry_pi5_image
        default:
          return ''
      }
    },
    board_connector() : string | undefined {
      const usbRoot = this.serial_port_path.split('-port0')[0]
      const connector = Object.entries(this.updated_connector_map).find(([key, _]) => usbRoot.includes(key))
      return connector?.[1]
    },
    usbOverlayInfo(): string | null {
      // This regex matches ...usb-0:1.4.3:1.0... and captures the last number before :1.0 (the hub port)
      const match = this.serial_port_path.match(/usb-0:(?:[0-9]+\.)+([0-9]+):1\.0/)
      if (match) {
        return `Connected via hub, device is on hub port ${match[1]}`
      }
      return null
    },
  },
  mounted() {
    // Wait for svg element to be loaded to set object
    let id = 0
    const name = `.${this.svgName}${this.inline ? '-inline' : ''}`
    id = setInterval(() => {
      const element = document?.querySelector(name) as HTMLEmbedElement | null
      if (element) {
        this.imgObject = element?.getSVGDocument()
        element!.onload = () => {
          this.imgObject = element?.getSVGDocument()
          const connector = this.board_connector
          if (connector !== undefined) {
            this.setSvgConnector(connector)
          }
        }
        this.updateImgObjectFromElement(element)
        clearInterval(id)
      }
    }, 500)
  },
  methods: {
    updateImgObjectFromElement(element: HTMLEmbedElement) {
      this.imgObject = element?.getSVGDocument()
      const connector = this.board_connector
      if (connector !== undefined) {
        this.setSvgConnector(connector)
      }
    },
    setSvgConnector(connector: string) {
      this.imgObject
        ?.getElementById(connector)
        ?.setAttribute('visibility', 'visible')
    },
  },
})
</script>

<style scoped>
.usb-overlay {
  position: absolute;
  top: 8px;
  left: 8px;
  background: rgba(0,0,0,0.7);
  color: #fff;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 14px;
  z-index: 10;
  pointer-events: none;
}
</style>
