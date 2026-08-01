# OBcar 共用生成指令

以下是通用長版模板；目前實際測試版本以 Saidio「產線 → OBcar」內可單獨複製的 Freed 三代 Demo Prompt 為準。每次先從實車參考照整理 `{{VEHICLE_IDENTITY_LOCK}}`，再替換 `{{MAKE_MODEL}}`、`{{SEATS}}`、`{{CAMERA_POSITION}}` 或 `{{DRONE_CAMERA_VIEW}}`。不能只替換車名：車色、世代、前後期、外觀套件、燈具、輪圈、門縫、徽章與車身比例都必須寫進 identity lock。

雙規格策略是先生成 16:9 主版本，同時保護畫面中央約 31.6% 寬度的 9:16 走廊。只有完整車身、四輪、車影與必要道路資訊能在整支片逐幀保留時，才直接裁成 9:16；若裁切令車太小、切掉車頭車尾或破壞運鏡，就依 Demo 的原生 9:16 重構 Prompt 另生直式版本。

## 1. 多角度定格圖共用模板

```text
Use all uploaded real vehicle photographs as strict immutable vehicle references.

Create one photorealistic automotive reference frame of the exact same {{MAKE_MODEL}}, {{SEATS}} seats.

VEHICLE IDENTITY — SINGLE SOURCE OF TRUTH:
{{VEHICLE_IDENTITY_LOCK}}

This is one fixed real-world vehicle parked inside one fixed, spatially coherent 360-degree environment. The vehicle remains locked to the exact same world coordinates, parking position and compass direction in every image. The four tyre contact points stay attached to the exact same points on the asphalt. The steering angle, wheels, doors, bonnet and tailgate do not move. Only the physical camera changes position around the stationary vehicle.

Buildings, road edges, parking lines, seawalls, lamp posts, trees, hills, coastline and horizon remain fixed in world space. Reconstruct the same location from the requested camera position with physically correct occlusion, perspective and parallax. Foreground objects shift more than distant objects; different sides of buildings may be revealed; parking lines converge differently; reflections update with the camera position. Never paste the same flat background behind a differently angled car.

DEFAULT ENVIRONMENT:
A geographically believable quiet seaside public parking area in northern Okinawa, Japan: clean Japanese asphalt, realistic white parking lines, a low concrete or stone seawall, calm blue-green sea, curved coastline, lush subtropical hills, simple dark lamp posts, sparse distant traffic and natural afternoon light. No generic resort, California or Mediterranean styling. The vehicle is never parked on sand.

CAMERA POSITION:
{{CAMERA_POSITION}}

LIGHTING LOCK:
Keep the exact same time of day, sun direction, weather, clouds, colour temperature, exposure and road condition across the full series. Vehicle and environmental shadows stay attached to their physical objects and remain consistent with one sun position.

TEXT POLICY:
No readable Japanese or English text, place names, shop names, road-sign wording, licence plate characters, prices, captions or watermarks. Any unavoidable sign is blank, turned away, hidden, distant or naturally out of focus. Use a plain blank white promotional licence plate. Preserve authentic factory badges only when supplied by the real references; do not invent or mutate them.

OUTPUT:
One single photorealistic automotive reference frame. Premium Japanese automotive advertising photography. No collage, contact sheet, labels, fisheye, extreme wide-angle stretching or motion blur.

STRICTLY FORBIDDEN:
rotating the vehicle, turntable photography, car spinning or pivoting, changing compass direction, changing tyre positions relative to parking lines, copying one flat background behind every view, mirroring, impossible coastline movement, nearby objects fixed in screen coordinates, missing parallax, inconsistent road or building orientation, changing sun direction, rotating the vehicle shadow, fake text, licence plate mutation, vehicle morphing, changing body length, height, doors, headlights, taillights or wheels.

The visible change in vehicle angle must come only from the camera physically moving inside the same fixed three-dimensional environment.
```

### 七個標準角度

依序逐張生成；每張都帶入主場景定錨圖、所有實車照及上一張批准圖。

```text
ANGLE 01 — FRONT LEFT
Front-left three-quarter view. Camera azimuth 35 degrees left of the vehicle's forward direction, radius 4.5 metres, height 0.9 metres, 50mm full-frame equivalent. Complete vehicle visible.

ANGLE 02 — LEFT PROFILE
Perfect left-side profile. Camera perpendicular to the left side, radius 5 metres, height 1.1 metres, 60mm full-frame equivalent. Wheels align naturally in perspective.

ANGLE 03 — REAR LEFT
Rear-left three-quarter view. Camera azimuth 145 degrees from the vehicle's forward direction, radius 4.5 metres, height 0.95 metres, 50mm full-frame equivalent.

ANGLE 04 — REAR
Perfect centred rear view. Camera aligned with the longitudinal centre line, radius 5 metres, height 1 metre, 60mm full-frame equivalent. Rear design appears symmetrical.

ANGLE 05 — REAR RIGHT
Rear-right three-quarter view. Camera azimuth 215 degrees from the vehicle's forward direction, radius 4.5 metres, height 0.95 metres, 50mm full-frame equivalent.

ANGLE 06 — RIGHT PROFILE
Perfect right-side profile. Camera perpendicular to the right side, radius 5 metres, height 1.1 metres, 60mm full-frame equivalent.

ANGLE 07 — FRONT RIGHT
Front-right three-quarter view. Camera azimuth 325 degrees from the vehicle's forward direction, radius 4.5 metres, height 0.9 metres, 50mm full-frame equivalent.
```

## 2. 定點 360°影片模板

每段放入物理上相容的 start frame 與 end frame。完整 360°依同一方向生成七段：Angle 01→02、02→03、03→04、04→05、05→06、06→07，以及 07 經車頭回到 01。

```text
Use the uploaded start frame and end frame as strict visual anchors.

Create a continuous photorealistic drone-camera movement between the two views of the exact same {{MAKE_MODEL}}.

IMPORTANT PHYSICAL RULE:
The vehicle is a fixed real-world object parked on the ground. The four tyre contact points, parking lines and vehicle shadow remain locked to the exact same physical coordinates throughout the clip. The vehicle does not translate, rotate, pivot, slide or float. Wheels do not roll and steering does not change.

This is NOT a rotating turntable product shot.

Only the physical camera travels through real three-dimensional space, like a stabilized cinematic drone flying around a stationary parked car. Infer the shortest natural flight path from the exact start-camera position to the exact end-camera position. Use real camera translation, a gentle continuous curve in one direction, approximately 0.8–2 metres camera height when compatible with the frames, a natural 40–50mm full-frame equivalent perspective and physically correct foreground/background parallax. Parking lines, coastline and nearby objects visibly shift through perspective.

No digital zoom, camera teleportation, movement through the vehicle, sudden reversal or orbit around a car that secretly rotates to face the camera. The changing vehicle view must be caused entirely by camera travel.

VEHICLE IDENTITY LOCK:
{{VEHICLE_IDENTITY_LOCK}}

Preserve the exact same parking bay, asphalt, parking lines, seawall, coastline, sea, hills, buildings, sky, sunlight and shadows. Do not add, remove or move background objects. The first frame closely matches the supplied start image; the final frame closely matches the supplied end image. Maintain gentle camera movement through the final frame so the next clip can continue naturally.

No readable signs, Japanese text, English text, licence plate characters, generated captions or watermarks. Keep signs blank, distant, hidden or naturally out of focus.

STRICTLY FORBIDDEN:
rotating turntable shot, vehicle rotating toward camera, pivoting or spinning in place, sliding over parking lines, wheels moving relative to asphalt, shadow rotating independently, static background while the vehicle angle changes, fake 2D image rotation, digital pan across a still, zoom-only movement, warped geometry, morphing wheels or camera teleportation.

The background must show real parallax caused by physical camera travel. The car remains completely fixed to the ground.
```

## 3. 海邊道路定格圖模板

```text
Use all uploaded real vehicle photographs as strict immutable references. The photographs are the single source of truth.

Create a premium photorealistic automotive advertising image featuring the exact same {{MAKE_MODEL}}, {{SEATS}} seats.

VEHICLE IDENTITY LOCK:
{{VEHICLE_IDENTITY_LOCK}}

Do not change the generation, body variant, trim, paint, grille, lights, bumpers, wheels, tyres, mirrors, windows, door seams, handles, taillights, hatch, badges or ride height. Do not add roof rails, wheel-arch cladding, body kits, spoilers, oversized wheels or accessories absent from the references.

Show the vehicle driving safely along a geographically believable coastal road in northern Okinawa, Japan: calm blue-green sea, curved coastline, low seawall, lush subtropical hills, clean Japanese asphalt, correct white road markings, left-side traffic and sparse ordinary traffic. No high-rise skyline, generic California or Mediterranean coastline, fantasy tropical beach or driving on sand.

DRONE CAMERA VIEW:
{{DRONE_CAMERA_VIEW}}

Use bright natural Okinawa afternoon light, realistic reflections and road shadow, believable sky and clouds, restrained colour, photorealistic Japanese automotive-commercial styling and sufficient road ahead. No text, captions, watermarks, readable road signs or licence plate characters.
```

### 海邊鏡頭選項

```text
A — HIGH WIDE ESTABLISHING
Very high wide aerial view, about 60 metres above the road, behind and diagonally toward the ocean side, 24mm equivalent. Vehicle small but identifiable; coastline dominates.

B — MEDIUM REAR TRACKING (DEFAULT)
Rear three-quarter drone view, about 12 metres above and 18 metres behind, slightly toward the ocean side, 35mm equivalent. Balanced vehicle, road and coastline.

C — ELEVATED SIDE TRACKING
About 8 metres above the road, parallel on the ocean side, full side and front three-quarter angle, 50mm equivalent. Vehicle is the main subject.

D — CLOSE FRONT THREE-QUARTER
About 4 metres above and 7 metres ahead, camera faces backward, 50mm equivalent. Vehicle fills about 55 percent of frame.

E — LOW REAR TRACKING
About 1.8 metres above and 6 metres behind, 70mm equivalent. Emphasize rear design, lights and wheels while retaining coastline.

F — TOP DOWN
Near-vertical top-down view, about 25 metres above. Vehicle follows the correct lane between sea and green hillside; no distorted proportions.
```

## 4. 海邊道路影片模板

```text
Animate the supplied image into a premium photorealistic automotive drone shot.

The exact {{MAKE_MODEL}} drives forward at a safe, steady road speed along the coastal road in northern Okinawa, following the correct left-side traffic lane. Wheels rotate forward at the correct speed, tyres remain attached to the road, the body follows the lane and suspension shows subtle realistic movement. The vehicle does not slide sideways, rotate independently, drift, change lanes or accelerate aggressively.

The drone preserves the reference image's visual angle and composition while physically flying through real three-dimensional space. Use stabilized tracking, realistic forward motion, constant or gently changing distance, smooth altitude control and natural background parallax. Coastline, road markings and light poles pass naturally. No sudden zoom, teleportation, stationary-car orbit or turntable effect.

VEHICLE IDENTITY LOCK:
{{VEHICLE_IDENTITY_LOCK}}

Preserve the blue-green sea, curved coastline, seawall, green hills, Japanese markings, natural daylight, left-side traffic and stable horizon. No vehicle morphing, colour change, wheel redesign, changing body length, extra doors, readable signs, licence plate characters, captions or watermarks.

Photorealistic Japanese automotive and travel commercial.
```

## 5. 可附加的海邊 Camera Motion

```text
DISTANT TO CLOSE:
Begin as a wide aerial establishing shot. The drone gradually descends and accelerates gently toward the moving vehicle, ending in a medium rear three-quarter tracking view. No digital zoom; size change comes only from flying closer.

CLOSE TO WIDE:
Begin close in a rear three-quarter tracking view. The drone climbs and flies backward, revealing coastline, road, sea and hills. The vehicle keeps a steady speed and becomes smaller only because of physical camera travel.

LOW REAR TO HIGH AERIAL:
Begin at a low rear three-quarter angle. Climb smoothly while continuing to follow, ending in a high diagonal aerial landscape view with continuous parallax.

OCEAN-SIDE TO FRONT:
Fly parallel on the ocean side. Begin in a medium-wide side profile, then move closer and slightly forward to an elevated front three-quarter tracking angle. Stay outside the driving lane; no sudden orbit or independent vehicle rotation.
```

## 6. 每款車的 identity lock 最低格式

```text
- exact make, model, market name, generation and model year
- exact body style and factory trim; standard/crossover/aero distinction
- exact seat configuration where externally relevant
- exact paint colour and finish
- exact grille/front panel, headlight/DRL and bumper design
- exact factory wheel design, tyre dimensions and ride height
- exact mirrors, window shape, pillars and black/chrome trim
- exact door count, sliding-door seams, handles and fuel-door position
- exact rear hatch, rear window, taillights, bumper and factory badge placement
- no accessories not visible in the approved real references
```

若其中任何一欄無法從照片或客戶資料確定，該車維持 `needs_spec` 或 `needs_references`，不要用模型常識補空白。
