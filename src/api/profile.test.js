import {
  beforeEach,
  describe,
  expect,
  it,
  vi,
} from 'vitest';
import {
  apiRequest,
} from './client';
import {
  calculateFashionDNA,
} from './profile';

vi.mock(
  './client',
  () => ({
    apiRequest: vi.fn(),
  }),
);

describe('profile API', () => {
  beforeEach(() => {
    apiRequest.mockReset();

    apiRequest.mockResolvedValue({
      profile_id:
        '0a984b56-eccc-4f12-8af9-5806a4912988',
      version: 1,
    });
  });

  it('uses the new atomic profile DNA endpoint', async () => {
    const answers = [
      {
        question_id: 'everyday-look',
        choice_id: 'minimal-campus',
      },
    ];

    await calculateFashionDNA(
      answers,
    );

    expect(
      apiRequest,
    ).toHaveBeenCalledTimes(1);

    expect(
      apiRequest,
    ).toHaveBeenCalledWith(
      '/api/profile/dna/calculate',
      {
        method: 'POST',
        body: JSON.stringify({
          answers,
        }),
      },
    );
  });

  it('does not use the old DNA endpoint', async () => {
    const answers = [
      {
        question_id: 'everyday-look',
        choice_id: 'minimal-campus',
      },
    ];

    await calculateFashionDNA(
      answers,
    );

    const calledPath =
      apiRequest.mock.calls[0][0];

    expect(calledPath).not.toBe(
      '/api/dna/calculate',
    );

    expect(calledPath).not.toBe(
      '/api/profile/dna',
    );
  });
});