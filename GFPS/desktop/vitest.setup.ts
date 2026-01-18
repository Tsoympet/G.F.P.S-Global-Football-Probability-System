import '@testing-library/jest-dom';
import { webcrypto } from 'crypto';

if (!(global as { crypto?: Crypto }).crypto) {
  (global as { crypto?: Crypto }).crypto = webcrypto as unknown as Crypto;
}
