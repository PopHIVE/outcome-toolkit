import L, { DomUtil } from "leaflet";

/*
 * Extension of L.Control to hook it up with VueJS. Not exposed because you should use the factory function below.
 */
const CustomControl = L.Control.extend({
  options: {
    // Dummy component until Vue hooks up the ref
    componentRef: DomUtil.create("div") as HTMLElement,
    position: "bottomright",
  },
  onAdd: function () {
    return this.options.componentRef;
  },
});

/**
 * Factory for creating a custom leaflet control. (Replaces vue-leaflet's <Control />.)
 *
 * See [Extending Classes (leaflet)](https://leafletjs.com/examples/extending/extending-1-classes.html)
 * and [StackOverflow](https://stackoverflow.com/questions/78617871/correct-way-to-extend-leaflet-classes-with-typescript).
 *
 * Usage:
 * ```
 *    const componentRef = ref<undefined | HTMLElement>();
 *    if (componentRef.value)
 *    const component = makeCustomControl(
 *      componentRef.value,
 *      { position: "bottomleft"}
 *    );
 *    component.addto(mapRef);
 *
 * ```
 * ```jsx
 *   <template>
 *     <div ref="componentRef">
 *       Contents of component go here.
 *     </div>
 *   </template>
 * ```
 */
export function makeCustomControl(componentRef: HTMLElement, options: L.ControlOptions) {
  const c = new CustomControl(options);
  c.options.componentRef = componentRef;
  return c;
}
