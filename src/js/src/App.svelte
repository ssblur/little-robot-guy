<script>
	let status = null;
	let animations = null;
	let animationTimeout = null;
	let hasEverHadTime = false;
	let frame = 0;
	let time = 0;
	let latest = 0;

	// Animations are fetched at start, with the concession that the page needs to be reloaded if the script is restarted.
	fetch("/animations", {method: "POST"})
		.then(response => response.json())
		.then(response => {
			animations = response;
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

	setInterval(
		() => {
			if(time > 0) time--;
			fetch("/time", {method: "POST"})
				.then(response => response.json())
				.then(response => {
					response = response.filter(item => item[0] > latest);
					for(let item of response) {
						latest = Math.max(latest, item[0]);
						time += item[1]
					}
					if(time > 0) hasEverHadTime = true;
				});
		},
		1000
	);

	/**
	 * Advances the current animation to the next frame.
	 * Queues a frame advance to occur after this frame's duration is up.
	 */
	function advanceFrame() {
		frame++;
		frame = frame % getAnimation().frames.length;
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

	function formatTime(seconds) {
		let date = new Date(0)
		date.setSeconds(seconds)
		return date.toISOString().substring(11, 19)
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

	.inactive {
		display: none;
	}

	.active { 
		display: block;
	}

	.time {
		position: fixed;
		right: 20px;
		top: 20px;
		font-size: 10vw;
		z-index: 100;
		font-family: 'Gill Sans', 'Gill Sans MT', Calibri, 'Trebuchet MS', sans-serif;
		color: white;
		background-color: #000;
		text-align: center;
		padding-top: 0;
		margin-top: 0;
	}

	.timelabel {
		font-size: 4vw;
		padding: 0;
		margin: 0;
	}
</style>

<div>
	{#if animations}
		{#each Object.entries(animations) as [key, animation]}
			<div class="{status == key ? 'active' : 'inactive'}">
				{#each Object.entries(animation.frames) as [index, framedata]}
					<div class="{frame == index ? 'active' : 'inactive'}">
						{#each framedata.layers as layer}
							{#if typeof layer == "string" || layer instanceof String}
								<img 
									src="layers/{layer}" 
									alt="Animation {key} frame {index} layer {layer}" />
							{:else}
								<img 
									src="layers/{layer.path}" 
									alt="Animation {key} frame {index} layer {layer.path}" />
							{/if}
						{/each}
					</div>
				{/each}
			</div>
		{/each}
	{/if}
	{#if hasEverHadTime}
		<div class="time">
			<p class="timelabel">Time Remaining</p>
			{formatTime(time)}
		</div>
	{/if}
</div>