import {
  useMemo,
  useState,
} from 'react';

import { useNavigate } from 'react-router-dom';

import {
  checkoutCart,
} from '../../api/events';

import { useUser } from '../../context/useUser';


function formatPrice(value) {
  return new Intl.NumberFormat(
    'en-IN',
    {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    },
  ).format(Number(value) || 0);
}


export default function Cart() {
  const navigate = useNavigate();

  const {
    user,
    clearCart,
  } = useUser();

  const [checkingOut, setCheckingOut] =
    useState(false);

  const [checkoutError, setCheckoutError] =
    useState('');

  const cart = useMemo(
    () => (
      Array.isArray(user.cartItems)
        ? user.cartItems
        : []
    ),
    [user.cartItems],
  );

  const cartTotal = useMemo(
    () => (
      cart.reduce(
        (total, item) => (
          total
          + (
            Number(item.price) || 0
          ) * (
            Number(item.quantity) || 1
          )
        ),
        0,
      )
    ),
    [cart],
  );

  const totalItems = useMemo(
    () => (
      cart.reduce(
        (total, item) => (
          total
          + (
            Number(item.quantity) || 1
          )
        ),
        0,
      )
    ),
    [cart],
  );

  async function handleCheckout() {
    if (cart.length === 0) {
      return;
    }

    setCheckingOut(true);
    setCheckoutError('');

    /*
     * Purchase memory is created only here.
     *
     * Merely adding an item to the cart must
     * never create a purchase or wardrobe item.
     */
    const checkoutItems = cart.map((item) => ({
      product_id: item.id,

      size:
        item.selectedSize
        ?? null,

      recommendation_item_id:
        item.recommendationItemId
        ?? null,

      decision_snapshot_id:
        item.decisionSnapshotId
        ?? null,
    }));

    try {
      await checkoutCart(
        checkoutItems,
      );

      clearCart();

      navigate('/memory');
    } catch (error) {
      console.error(
        'Checkout failed:',
        error,
      );

      setCheckoutError(
        error?.message
        ?? (
          'Checkout could not be completed. '
          + 'Please try again.'
        ),
      );
    } finally {
      setCheckingOut(false);
    }
  }

  if (cart.length === 0) {
    return (
      <main style={styles.page}>
        <section style={styles.emptyCard}>
          <div style={styles.emptyIcon}>
            🛍️
          </div>

          <h1 style={styles.emptyHeading}>
            Your cart is empty
          </h1>

          <p style={styles.emptyText}>
            Add products that match your Fashion
            DNA and return here to complete your
            purchase.
          </p>

          <button
            type="button"
            style={styles.primaryButton}
            onClick={() => navigate('/')}
          >
            Continue shopping
          </button>
        </section>
      </main>
    );
  }

  return (
    <main style={styles.page}>
      <header style={styles.header}>
        <div>
          <p style={styles.eyebrow}>
            MYNTRA IDENTITY
          </p>

          <h1 style={styles.heading}>
            Your Cart
          </h1>

          <p style={styles.subtitle}>
            {totalItems}{' '}
            {totalItems === 1
              ? 'item'
              : 'items'}{' '}
            ready for checkout
          </p>
        </div>

        <button
          type="button"
          style={styles.clearButton}
          disabled={checkingOut}
          onClick={clearCart}
        >
          Clear cart
        </button>
      </header>

      <div style={styles.layout}>
        <section style={styles.itemsSection}>
          {cart.map((item) => {
            const quantity =
              Number(item.quantity) || 1;

            return (
              <article
                key={[
                  item.id,
                  item.selectedSize ?? 'no-size',
                ].join('-')}
                style={styles.cartItem}
              >
                <div style={styles.imageWrapper}>
                  <img
                    src={item.image}
                    alt={item.name}
                    style={styles.image}
                  />
                </div>

                <div style={styles.itemDetails}>
                  <p style={styles.brand}>
                    {item.brand}
                  </p>

                  <h2 style={styles.itemName}>
                    {item.name}
                  </h2>

                  <div style={styles.itemMetadata}>
                    <span>
                      Size:{' '}
                      {item.selectedSize ?? 'Default'}
                    </span>

                    <span>
                      Quantity: {quantity}
                    </span>
                  </div>

                  {item.confidence?.overall != null && (
                    <p style={styles.confidence}>
                      {item.confidence.overall}% Fashion
                      DNA match
                    </p>
                  )}
                </div>

                <div style={styles.itemPrice}>
                  <strong>
                    {formatPrice(
                      (
                        Number(item.price) || 0
                      ) * quantity,
                    )}
                  </strong>

                  {quantity > 1 && (
                    <span style={styles.unitPrice}>
                      {formatPrice(item.price)} each
                    </span>
                  )}
                </div>
              </article>
            );
          })}
        </section>

        <aside style={styles.summary}>
          <p style={styles.summaryEyebrow}>
            ORDER SUMMARY
          </p>

          <h2 style={styles.summaryHeading}>
            Checkout
          </h2>

          <div style={styles.summaryRow}>
            <span>
              Items ({totalItems})
            </span>

            <span>
              {formatPrice(cartTotal)}
            </span>
          </div>

          <div style={styles.summaryRow}>
            <span>
              Delivery
            </span>

            <span style={styles.freeDelivery}>
              Free
            </span>
          </div>

          <div style={styles.divider} />

          <div style={styles.totalRow}>
            <span>
              Total
            </span>

            <span>
              {formatPrice(cartTotal)}
            </span>
          </div>

          {checkoutError && (
            <div
              role="alert"
              style={styles.error}
            >
              {checkoutError}
            </div>
          )}

          <button
            type="button"
            style={{
              ...styles.primaryButton,
              ...styles.checkoutButton,
              ...(checkingOut
                ? styles.disabledButton
                : {}),
            }}
            disabled={checkingOut}
            onClick={handleCheckout}
          >
            {checkingOut
              ? 'Completing purchase...'
              : 'Complete purchase'}
          </button>

          <p style={styles.checkoutNote}>
            Your purchase will be added to Fashion
            Memory only after checkout succeeds.
          </p>
        </aside>
      </div>
    </main>
  );
}


const styles = {
  page: {
    width: 'min(1180px, calc(100% - 32px))',
    margin: '0 auto',
    padding: '48px 0 80px',
  },

  header: {
    display: 'flex',
    alignItems: 'flex-end',
    justifyContent: 'space-between',
    gap: '24px',
    marginBottom: '32px',
  },

  eyebrow: {
    margin: '0 0 8px',
    fontSize: '12px',
    fontWeight: 700,
    letterSpacing: '0.16em',
    color: '#ff3f6c',
  },

  heading: {
    margin: 0,
    fontSize: 'clamp(32px, 5vw, 52px)',
    lineHeight: 1.05,
    color: '#202124',
  },

  subtitle: {
    margin: '12px 0 0',
    color: '#6b7280',
  },

  layout: {
    display: 'grid',
    gridTemplateColumns:
      'minmax(0, 1fr) minmax(280px, 360px)',
    gap: '28px',
    alignItems: 'start',
  },

  itemsSection: {
    display: 'grid',
    gap: '16px',
  },

  cartItem: {
    display: 'grid',
    gridTemplateColumns: '128px 1fr auto',
    gap: '20px',
    padding: '18px',
    border: '1px solid #ececf1',
    borderRadius: '22px',
    background: '#ffffff',
    boxShadow:
      '0 12px 40px rgba(31, 35, 48, 0.06)',
  },

  imageWrapper: {
    width: '128px',
    height: '152px',
    overflow: 'hidden',
    borderRadius: '16px',
    background: '#f5f5f7',
  },

  image: {
    width: '100%',
    height: '100%',
    objectFit: 'cover',
  },

  itemDetails: {
    minWidth: 0,
    padding: '8px 0',
  },

  brand: {
    margin: 0,
    fontSize: '13px',
    fontWeight: 700,
    color: '#ff3f6c',
  },

  itemName: {
    margin: '7px 0 12px',
    fontSize: '20px',
    lineHeight: 1.25,
    color: '#202124',
  },

  itemMetadata: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '8px 18px',
    fontSize: '14px',
    color: '#6b7280',
  },

  confidence: {
    display: 'inline-block',
    margin: '15px 0 0',
    padding: '7px 10px',
    borderRadius: '999px',
    background: '#f1f8f4',
    fontSize: '13px',
    fontWeight: 600,
    color: '#17834f',
  },

  itemPrice: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'flex-end',
    gap: '6px',
    paddingTop: '8px',
    fontSize: '18px',
    color: '#202124',
  },

  unitPrice: {
    fontSize: '12px',
    fontWeight: 400,
    color: '#8a8f98',
  },

  summary: {
    position: 'sticky',
    top: '24px',
    padding: '26px',
    border: '1px solid #ececf1',
    borderRadius: '24px',
    background: '#ffffff',
    boxShadow:
      '0 16px 50px rgba(31, 35, 48, 0.08)',
  },

  summaryEyebrow: {
    margin: 0,
    fontSize: '11px',
    fontWeight: 700,
    letterSpacing: '0.15em',
    color: '#ff3f6c',
  },

  summaryHeading: {
    margin: '8px 0 24px',
    fontSize: '27px',
    color: '#202124',
  },

  summaryRow: {
    display: 'flex',
    justifyContent: 'space-between',
    gap: '20px',
    marginBottom: '16px',
    fontSize: '15px',
    color: '#626771',
  },

  freeDelivery: {
    fontWeight: 700,
    color: '#17834f',
  },

  divider: {
    height: '1px',
    margin: '22px 0',
    background: '#ececf1',
  },

  totalRow: {
    display: 'flex',
    justifyContent: 'space-between',
    gap: '20px',
    fontSize: '21px',
    fontWeight: 700,
    color: '#202124',
  },

  primaryButton: {
    border: 0,
    borderRadius: '14px',
    padding: '14px 20px',
    background:
      'linear-gradient(135deg, #ff3f6c, #ff6f61)',
    color: '#ffffff',
    fontSize: '15px',
    fontWeight: 700,
    cursor: 'pointer',
  },

  checkoutButton: {
    width: '100%',
    marginTop: '26px',
  },

  disabledButton: {
    opacity: 0.65,
    cursor: 'not-allowed',
  },

  clearButton: {
    border: '1px solid #e3e3e8',
    borderRadius: '12px',
    padding: '11px 16px',
    background: '#ffffff',
    color: '#535862',
    fontWeight: 600,
    cursor: 'pointer',
  },

  error: {
    marginTop: '18px',
    padding: '12px',
    border: '1px solid #fecaca',
    borderRadius: '12px',
    background: '#fff1f2',
    color: '#b42318',
    fontSize: '14px',
    lineHeight: 1.45,
  },

  checkoutNote: {
    margin: '14px 0 0',
    fontSize: '12px',
    lineHeight: 1.5,
    textAlign: 'center',
    color: '#858b95',
  },

  emptyCard: {
    maxWidth: '600px',
    margin: '80px auto',
    padding: '56px 32px',
    border: '1px solid #ececf1',
    borderRadius: '28px',
    background: '#ffffff',
    textAlign: 'center',
    boxShadow:
      '0 18px 60px rgba(31, 35, 48, 0.08)',
  },

  emptyIcon: {
    marginBottom: '18px',
    fontSize: '52px',
  },

  emptyHeading: {
    margin: 0,
    fontSize: '32px',
    color: '#202124',
  },

  emptyText: {
    maxWidth: '440px',
    margin: '14px auto 26px',
    lineHeight: 1.7,
    color: '#6b7280',
  },
};
