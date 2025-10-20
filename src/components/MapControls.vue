<template>
  <div class="container mt-4">
    <div class="row justify-content-center">
      <div class="col-auto">
        <!-- Stack controls vertically -->
        <div class="d-flex flex-column align-items-center">
          <!-- Row: Min Population + Checkbox -->
          <div class="d-flex flex-row align-items-center mb-2">
            <!-- Minimum Population Filter -->
            <label class="form-label mb-0 me-3">
              Minimum Population:
              <input
                type="number"
                :value="minPopulation"
                @input="$emit('update:minPopulation', Number($event.target.value))"
                min="0"
                step="500"
                class="form-control d-inline-block ms-2"
                style="width: 120px;"
              />
            </label>
            <!-- Equal Radius Checkbox -->
            <div class="form-check ms-3">
              <input
                class="form-check-input"
                type="checkbox"
                id="equalRadius"
                :checked="equalRadiusMode"
                @change="$emit('update:equalRadiusMode', $event.target.checked)"
              />
              <label class="form-check-label" for="equalRadius">
                Equal Dot Sizes
              </label>
            </div>
          </div>
          <!-- Slider and Year Label below -->
          <input
            type="range"
            :min="startYear"
            :max="endYear"
            :value="currentYear"
            @input="$emit('update:currentYear', Number($event.target.value))"
            step="10"
            class="form-range"
            style="width: 600px;"
          />
          <div class="fw-bold fs-2 mt-2">
            Year: {{ currentYear }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "MapControls",
  props: {
    currentYear: {
      type: [Number, String],
      default: 1910
    },
    minPopulation: {
      type: Number,
      default: 2500
    },
    equalRadiusMode: {
      type: Boolean,
      default: false
    },
    // define slider range props (accept strings too if parent passes them as such)
    startYear: {
      type: [Number, String],
      default: 1910
    },
    endYear: {
      type: [Number, String],
      default: 2020
    }
  },
  emits: ['update:minPopulation', 'update:equalRadiusMode', 'update:currentYear']
};
</script>