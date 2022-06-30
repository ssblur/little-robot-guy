<script>
	let status = null;
	let animations = null;
	let animationTimeout = null;
	let frame = 0;
	let layers = [];
	let activeFrames = []

	// Animations are fetched at start, with the concession that the page needs to be reloaded if the script is restarted.
	fetch("/animations", {method: "POST"})
		.then(response => response.json())
		.then(response => {
			animations = response;
			for(let animation of Object.values(animations))
				for(let frame of animation.frames)
					for(let layer of frame.layers) {
						let path;
						if(typeof layer === 'string' || layer instanceof String)
							path = layer;
						else
							path = layer.path;
						if(!(path in layers))
							layers.push(path);
					}
		});

	// Rather than streaming animation data, the same HTTP server is just used to sync animation state.
	// This is updated 20 times per second.
	setInterval(
		() => {
			fetch("/status", {method: "POST"})
				.then(response => response.json())
				.then(response => {
					if(status != response) {
						if(animationTimeout != null)
							clearInterval(animationTimeout);
						frame = 0;
						animationTimeout = setTimeout(advanceFrame, 1)
						status = response
					}
				});
		},
		50
	);

	/**
	 * Advances the current animation to the next frame.
	 * Queues a frame advance to occur after this frame's duration is up.
	 */
	function advanceFrame() {
		frame++;
		frame = frame % getAnimation().frames.length;
		activeFrames = getFrame().layers;
		animationTimeout = setTimeout(advanceFrame, getFrameLength())
	}

	/**
	 * Helper function for getting the current frame's intended duration.
	 */
	function getFrameLength() {
		return (getFrame()?.frame_duration || getAnimation()?.frame_duration || 1) * 1000;
	}

	/**
	 * Helper function for getting information on the current animation state.
	 */
	function getAnimation() {
		return animations && animations[status];
	}

	/**
	 * Helper function for getting information on the current frame.
	 */
	function getFrame() {
		return getAnimation()?.frames[frame] || null;
	}
</script>

<style>
	img {
		position: absolute;
		top: 0;
		left: 0;
		max-width: 100%;
		max-height: 100%;
	}

	img.inactive {
		display: none;
	}
</style>

{#each layers as layer}
	<img 
		src="layers/{layer}" 
		class="inactive" 
		alt="Animation placeholder {layer} for chat bot" />
{/each}

<div>
	{#if animations != null && status != null}
		{#each activeFrames as layer}
			<img 
				src="layers/{layer}" 
				alt="Animation layer {layer} for chat bot {frame}" />
		{/each}
	{:else}
		Loading...
	{/if}
</div>