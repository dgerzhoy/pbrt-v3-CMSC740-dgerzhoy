
/*
	pbrt source code is Copyright(c) 1998-2016
						Matt Pharr, Greg Humphreys, and Wenzel Jakob.

	This file is part of pbrt.

	Redistribution and use in source and binary forms, with or without
	modification, are permitted provided that the following conditions are
	met:

	- Redistributions of source code must retain the above copyright
	  notice, this list of conditions and the following disclaimer.

	- Redistributions in binary form must reproduce the above copyright
	  notice, this list of conditions and the following disclaimer in the
	  documentation and/or other materials provided with the distribution.

	THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
	IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
	TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
	PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
	HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
	SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
	LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
	DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
	THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
	(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
	OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

 */


 // integrators/directlighting.cpp*
#include "integrators/depthmap.h"
#include "interaction.h"
#include "paramset.h"
#include "camera.h"
#include "film.h"
#include "stats.h"

namespace pbrt {

    float DepthMapIntegrator::maxDist(const Ray ray, const Scene scene) const
	{
        Point3f pMax = scene.WorldBound().pMax;
        Point3f pMin = scene.WorldBound().pMin;
		Point3f o = ray.o;

		Point3f max;
		for (int i = 0; i < 3; i++)
		{
            Float oMax = (pMax[i] - o[i]);
            Float oMin = (pMin[i] - o[i]);
			if ( fabs(oMax) < fabs(oMin) ) 
			{
				max[i] = pMin[i];
            } else {
                max[i] = pMax[i];
			}
		}

        return Distance(o, max);
	}

	// DepthMapIntegrator Method Definitions
	void DepthMapIntegrator::Preprocess(const Scene &scene,
		Sampler &sampler) {
		//Point3f pMax = scene.WorldBound().pMax;
		//Point3f pMin = scene.WorldBound().pMin;
        //Point3f ctw = camera->CameraToWorld;
        //maxDistance = Distance(pMin, pMax);
        //printf("pMin %f %f %f | pMax %f %f %f\n", pMin.x, pMin.y, pMin.z,
        //       pMax.x, pMax.y, pMax.z);
	}
	Spectrum DepthMapIntegrator::Li(const RayDifferential &ray,
		const Scene &scene, Sampler &sampler,
		MemoryArena &arena, int depth) const 
	{
		ProfilePhase p(Prof::SamplerIntegratorLi);
        Spectrum Black(0.f);
        Spectrum White(1.f);
        Spectrum L;
        
        L = Black;
		// Find closest ray intersection or return background 0
		SurfaceInteraction isect;
		if (!scene.Intersect(ray, &isect)) {
			return L;
		}
		
		Point3f pMax = scene.WorldBound().pMax;
        Point3f pMin = scene.WorldBound().pMin;
        //Float maxDistance = Distance(pMin, pMax);
        //Float maxDistance = 100.f;
        Float maxDistance = maxDist(ray,scene);

		float dist = ray.tMax;
        float ratio = 1.f - dist / maxDistance;
		L = White * ratio;

		return L;
	}

	DepthMapIntegrator *CreateDepthMapIntegrator(
		const ParamSet &params, std::shared_ptr<Sampler> sampler,
		std::shared_ptr<const Camera> camera) {
		int maxDepth = params.FindOneInt("maxdepth", 5);
		int np;
		const int *pb = params.FindInt("pixelbounds", &np);
		Bounds2i pixelBounds = camera->film->GetSampleBounds();
		if (pb) {
			if (np != 4)
				Error("Expected four values for \"pixelbounds\" parameter. Got %d.",
					np);
			else {
				pixelBounds = Intersect(pixelBounds,
					Bounds2i{ {pb[0], pb[2]}, {pb[1], pb[3]} });
				if (pixelBounds.Area() == 0)
					Error("Degenerate \"pixelbounds\" specified.");
			}
		}
		return new DepthMapIntegrator(maxDepth, camera, sampler,
			pixelBounds);
	}

}  // namespace pbrt
