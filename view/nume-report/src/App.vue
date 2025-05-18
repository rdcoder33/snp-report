<template>
  <div>
    <div v-if="!streaming" class="space-y-6 p-6 bg-gray-50 rounded-lg shadow-md">
      <!-- Drop Zone -->
      <div
        class="drop-zone border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer transition-all hover:bg-gray-100"
        @dragover.prevent="dragOver"
        @dragleave.prevent="dragLeave"
        @drop.prevent="handleDrop"
        @click="triggerFileInput"
        :class="{ 'bg-blue-50 border-blue-400': isDragging }"
      >
        <p v-if="!selectedFile" class="text-gray-600">Drag and drop your file here or click to browse.</p>
        <p v-if="selectedFile" class="text-gray-700 font-medium">Selected file: {{ selectedFile.name }}</p>
        <input
          type="file"
          ref="fileInput"
          @change="handleFileUpload"
          accept=".txt"
          style="display: none;"
        />
      </div>

      <!-- Text Field -->
      <div>
        <label for="userProfile" class="block text-sm font-medium text-gray-700 mb-1">Options (User Profile):</label>
        <input
          id="userProfile"
          v-model="userProfile"
          type="text"
          placeholder="Enter user profile or options"
          class="w-full border border-gray-300 rounded-md p-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <!-- Upload Button -->
      <div v-if="selectedFile">
        <button
          @click="uploadFile"
          class="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition"
        >
          Upload
        </button>
      </div>
    </div>


    <div v-if="streaming">
      <div v-if="steps.length > 0 || reportSections.length > 0">
        <div v-if="steps.length > 0" class="processing-steps">
          <h3>Processing Steps:</h3>
          <ul class="steps-list">
            <li v-for="(step, idx) in steps" :key="'step-' + idx">
              <span class="step-icon active">🟢</span>
              <span class="step-text">{{ step }}</span>
            </li>
          </ul>
        </div>

        <div v-if="reportSections.length > 0" class="report-sections">
          <iframe
            ref="reportIframe"
            style="width:960px; border:none;"
            :style="{height: iframeHeight + 'px'}"
            @load="onIframeLoad"
          ></iframe>
        </div>
      </div>
      
      <p v-if="connectionStatus" class="connection-status">
        Status: {{ connectionStatus }}
      </p>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      selectedFile: null,
      isDragging: false,
      streaming: false,
      steps: [],
      reportSections: [],
      connectionStatus: null,
      iframeHeight: 400,
      userProfile: '',
    };
  },
  watch: {
    reportSections: {
      handler() {
        this.updateIframeContent();
      },
      deep: true,
    },
  },
  methods: {
    triggerFileInput() {
      this.$refs.fileInput.click();
    },
    handleFileUpload(event) {
      const files = event.target.files || event.dataTransfer.files;
      if (files.length > 0) {
        this.selectedFile = files[0];
      }
    },
    async uploadFile() {
      if (!this.selectedFile) return;
      
      this.streaming = true;
      this.steps = [];
      this.reportSections = [];
      this.connectionStatus = 'Processing started...';

      try {
        const fileContent = await this.readFile(this.selectedFile);
        await this.startStreaming(fileContent);
      } catch (error) {
        this.connectionStatus = `Error: ${error.message}`;
        this.streaming = false;
      }
    },
    readFile(file) {
      return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = e => resolve(e.target.result);
        reader.onerror = reject;
        reader.readAsText(file);
      });
    },
    async startStreaming(fileContent) {
      try {
        const response = await fetch('http://localhost:8000/stream-report', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            file_content: fileContent,
            user_profile: this.userProfile,
            file_type: 'type_23andme'
          }),
        });

        const reader = response.body
          .pipeThrough(new TextDecoderStream())
          .getReader();

        let buffer = '';
        while (true) {
          const { value, done } = await reader.read();
          if (done) break;
          
          buffer += value;
          const events = buffer.split('\n\n');
          buffer = events.pop() || '';

          for (const event of events) {
            const dataString = event.replace(/^data: /, '');
            try {
              const data = JSON.parse(dataString);
              
              // Handle current_action updates
              const nodeKey = Object.keys(data)[0];
              console.log(nodeKey);
              const nodeData = data[nodeKey];
              console.log(nodeData);
              if (nodeData.current_action) {
                this.addUniqueStep(nodeData.current_action);
              }
              
              // Handle report sections
              if (nodeData.report_sections_ui?.length) {
                nodeData.report_sections_ui.forEach(section => {
                  if (!this.reportSections.includes(section)) {
                    this.reportSections = [...this.reportSections, section];
                  }
                });
              }
            } catch (error) {
              console.error('Error parsing event:', error);
            }
          }
        }
        
        this.connectionStatus = 'Processing complete';
      } catch (error) {
        this.connectionStatus = `Stream error: ${error.message}`;
        throw error;
      }
    },
    addUniqueStep(step) {
      if (!this.steps.includes(step)) {
        this.steps = [...this.steps, step];
      }
    },
    dragOver() {
      this.isDragging = true;
    },
    dragLeave() {
      this.isDragging = false;
    },
    handleDrop(event) {
      this.isDragging = false;
      const files = event.dataTransfer.files;
      if (files.length > 0) {
        this.selectedFile = files[0];
      }
    },
    updateIframeContent() {
      this.$nextTick(() => {
        const iframe = this.$refs.reportIframe;
        if (!iframe) return;
        const doc = iframe.contentDocument || iframe.contentWindow.document;
        if (!doc) return;
        doc.open();
        doc.write(this.reportHtml());
        doc.close();
        this.setIframeHeight();
      });
    },
    setIframeHeight() {
      this.$nextTick(() => {
        const iframe = this.$refs.reportIframe;
        if (!iframe) return;
        const doc = iframe.contentDocument || iframe.contentWindow.document;
        if (!doc) return;
        setTimeout(() => {
          this.iframeHeight = doc.body.scrollHeight;
        }, 100);
      });
    },
    onIframeLoad() {
      this.setIframeHeight();
    },
    reportHtml() {
      return `
        <html>
        <head>
          <link href=\"https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css\" rel=\"stylesheet\">
          <style>body { margin: 0; background: #f9fafb; }</style>
        </head>
        <body>
          <div class=\"container mx-auto px-4 py-8 max-w-6xl\">
            <!-- Report Header -->
            <div class=\"bg-white shadow-md rounded-lg overflow-hidden mb-8\">
                <div class=\"bg-blue-700 px-6 py-4\">
                    <div class=\"flex justify-between items-center\">
                        <h1 class=\"text-2xl font-bold text-white\">Genetic Testing Report</h1>
                        <div class=\"text-white text-sm\">Report Date: May 18, 2025</div>
                    </div>
                </div>
                <div class=\"p-6 grid grid-cols-1 md:grid-cols-2 gap-6\">
                    <!-- Patient Information -->
                    <div>
                        <h2 class=\"text-lg font-semibold text-gray-800 mb-2\">Patient Information</h2>
                        <div class=\"bg-gray-50 p-4 rounded-md\">
                            <div class=\"grid grid-cols-2 gap-2 text-sm\">
                                <div class=\"text-gray-600\">Name:</div>
                                <div class=\"font-medium\">[Patient Name]</div>
                                <div class=\"text-gray-600\">DOB:</div>
                                <div class=\"font-medium\">[Date of Birth]</div>
                                <div class=\"text-gray-600\">ID:</div>
                                <div class=\"font-medium\">[Patient ID]</div>
                                <div class=\"text-gray-600\">Sex:</div>
                                <div class=\"font-medium\">[Sex]</div>
                            </div>
                        </div>
                    </div>
                    <!-- Laboratory Information -->
                    <div>
                        <h2 class=\"text-lg font-semibold text-gray-800 mb-2\">Laboratory Information</h2>
                        <div class=\"bg-gray-50 p-4 rounded-md\">
                            <div class=\"grid grid-cols-2 gap-2 text-sm\">
                                <div class=\"text-gray-600\">Lab Name:</div>
                                <div class=\"font-medium\">Genomic Health Laboratories</div>
                                <div class=\"text-gray-600\">Specimen Type:</div>
                                <div class=\"font-medium\">Saliva</div>
                                <div class=\"text-gray-600\">Collection Date:</div>
                                <div class=\"font-medium\">May 11, 2025</div>
                                <div class=\"text-gray-600\">Report ID:</div>
                                <div class=\"font-medium\">GTR-25051812</div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class=\"bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-4\">
                    <div class=\"flex\">
                        <div class=\"flex-shrink-0\">
                            <svg class=\"h-5 w-5 text-yellow-400\" xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 20 20\" fill=\"currentColor\">
                                <path fill-rule=\"evenodd\" d=\"M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z\" clip-rule=\"evenodd\" />
                            </svg>
                        </div>
                        <div class=\"ml-3\">
                            <p class=\"text-sm text-yellow-700\">
                                This report is for informational use only. Talk to a healthcare professional before making any changes to your health routine.
                            </p>
                        </div>
                    </div>
                </div>
            </div>
            ${this.reportSections.map((section) => `<div class=\"report-section\">${section}</div>`).join('')}
            <!-- Footer -->
            <div class=\"mt-8 text-center text-gray-500 text-sm\">
                <p>This report is for informational purposes only and should not replace medical advice from a healthcare professional.</p>
                <p class=\"mt-2\">Report generated on May 18, 2025 • GenomicHealth Report ID: GTR-25051812</p>
            </div>
          </div>
        </body>
        </html>
      `;
    },
  },
};
</script>

<style scoped>
/* Drop zone */
.drop-zone {
  border: 2px dashed #ccc;
  padding: 3rem;
  text-align: center;
  cursor: pointer;
  margin: 1.5rem 0;
  border-radius: 10px;
  background-color: #f9f9f9;
  transition: all 0.3s ease;
  font-size: 1rem;
  color: #555;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
}

.drop-zone.dragging {
  border-color: #42b983;
  background-color: rgba(66, 185, 131, 0.1);
  color: #2f855a;
}

/* Text input */
input[type="text"] {
  width: 100%;
  padding: 0.75rem 1rem;
  margin-top: 0.5rem;
  font-size: 1rem;
  border: 1px solid #ccc;
  border-radius: 8px;
  outline: none;
  transition: border-color 0.3s, box-shadow 0.3s;
}

input[type="text"]:focus {
  border-color: #42b983;
  box-shadow: 0 0 0 2px rgba(66, 185, 131, 0.2);
}

/* Button */
button {
  background: #42b983;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.3s ease, transform 0.2s;
  margin-top: 1rem;
}

button:hover {
  background: #3aa876;
  transform: translateY(-1px);
}

/* Steps list */
.steps-list {
  list-style: none;
  padding: 0;
  margin: 1.5rem 0;
}

.steps-list li {
  padding: 0.5rem 0;
  display: flex;
  align-items: center;
  font-size: 0.95rem;
}

.step-icon {
  margin-right: 0.75rem;
}

/* Connection status */
.connection-status {
  color: #666;
  font-size: 0.9em;
  margin-top: 1rem;
}
</style>
