import fs from 'node:fs';
import path from 'node:path';

import {
  describe,
  expect,
  it,
} from 'vitest';

import {
  quizQuestions,
} from './quizQuestions';

describe('quiz image assets', () => {
  it(
    'has a local image for every choice',
    () => {
      for (
        const question
        of quizQuestions
      ) {
        for (
          const choice
          of question.choices
        ) {
          expect(
            choice.image.startsWith(
              '/quiz/',
            ),
          ).toBe(true);

          const relativeImagePath =
            choice.image.replace(
              /^\/+/,
              '',
            );

          const imagePath = path.join(
            process.cwd(),
            'public',
            relativeImagePath,
          );

          expect(
            fs.existsSync(imagePath),
            `Missing quiz asset: ${
              choice.image
            }`,
          ).toBe(true);
        }
      }
    },
  );

  it(
    'has a local fallback image',
    () => {
      const fallbackPath = path.join(
        process.cwd(),
        'public',
        'quiz',
        'fallback.webp',
      );

      expect(
        fs.existsSync(
          fallbackPath,
        ),
      ).toBe(true);
    },
  );
});
