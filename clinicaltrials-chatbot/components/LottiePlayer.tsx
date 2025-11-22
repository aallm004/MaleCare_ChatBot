"use client";

import React from "react";
import { DotLottieReact } from '@lottiefiles/dotlottie-react';

interface LottiePlayerProps {
  src: string;
  loop?: boolean;
  autoplay?: boolean;
  className?: string;
}

export default function LottiePlayer({ src, loop = true, autoplay = true, className }: LottiePlayerProps) {
  return (
    <div className={className}>
      <DotLottieReact src={src} loop={loop} autoplay={autoplay} />
    </div>
  );
}
